import base64
import importlib.util
import json
import zipfile
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "extract_docx_outline.py"


def load_module():
    spec = importlib.util.spec_from_file_location("extract_docx_outline", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def require_docx():
    return pytest.importorskip("docx")


def write_png(path: Path):
    data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lHk3"
        "6QAAAABJRU5ErkJggg=="
    )
    path.write_bytes(data)


def build_sample_docx(path: Path):
    docx = require_docx()
    doc = docx.Document()
    doc.add_heading("基于转录组数据探究脓毒症诊断标志物", level=1)
    doc.add_paragraph("项目编号：project-test-0001转录组诊断")
    doc.add_heading("背景", level=1)
    doc.add_paragraph("本研究关注脓毒症（Sepsis）外周血转录组诊断标志物。")
    doc.add_heading("方法", level=1)
    doc.add_paragraph("1）鉴定SP中的DEGs；")
    doc.add_paragraph("2）WGCNA分析；")
    doc.add_paragraph("3）使用机器学习筛选特征基因；")
    doc.add_heading("数据分析", level=1)
    doc.add_paragraph("数据准备：训练集：GSE185263数据集；样本类型：全血；348例SP vs 44例正常；用途：DEGs和WGCNA。PMID: 35027333")
    doc.add_paragraph("Fig.1 火山图和热图示例")
    image_path = path.with_suffix(".png")
    write_png(image_path)
    doc.add_picture(str(image_path))
    doc.add_paragraph("参考文献：PMID: 38291374")
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "数据集"
    table.cell(0, 1).text = "用途"
    table.cell(1, 0).text = "GSE154918"
    table.cell(1, 1).text = "验证集"
    doc.save(path)


def test_extract_docx_outline_detects_core_fields(tmp_path):
    module = load_module()
    docx_path = tmp_path / "sample.docx"
    out_dir = tmp_path / "out"
    build_sample_docx(docx_path)

    result = module.extract_docx(docx_path, out_dir)

    assert result["source_file"].endswith("sample.docx")
    assert "基于转录组数据探究脓毒症诊断标志物" in result["title_candidates"]
    assert result["project_id"] == "project-test-0001转录组诊断"
    assert "GSE185263" in result["dataset_ids"]
    assert "GSE154918" in result["dataset_ids"]
    assert "35027333" in result["pmids"]
    assert "38291374" in result["pmids"]
    assert any(module_item["name"] == "差异表达分析" for module_item in result["method_modules"])
    assert any(module_item["name"] == "WGCNA" for module_item in result["method_modules"])
    assert any(module_item["name"] == "机器学习诊断模型" for module_item in result["method_modules"])
    assert result["image_rule"] == "Embedded Word images are reference figure types only, not real analysis results."
    assert result["tables"][0]["rows"][1] == ["GSE154918", "验证集"]


def test_extract_docx_outline_extracts_images_as_reference_figures(tmp_path):
    module = load_module()
    docx_path = tmp_path / "sample.docx"
    out_dir = tmp_path / "out"
    build_sample_docx(docx_path)

    result = module.extract_docx(docx_path, out_dir)

    assert len(result["figures"]) == 1
    figure = result["figures"][0]
    assert figure["is_reference_only"] is True
    assert figure["figure_type"] in {"volcano plot", "heatmap"}
    extracted_path = Path(figure["extracted_path"])
    assert extracted_path.exists()
    assert extracted_path.is_relative_to(out_dir)
    assert "Fig.1 火山图和热图示例" in figure["previous_text"]


def test_extract_docx_outline_extracts_images_inside_tables(tmp_path):
    docx = require_docx()
    module = load_module()
    docx_path = tmp_path / "table-image.docx"
    image_path = tmp_path / "table-image.png"
    out_dir = tmp_path / "out"
    write_png(image_path)

    doc = docx.Document()
    doc.add_heading("表格图片测试", level=1)
    table = doc.add_table(rows=1, cols=1)
    cell = table.cell(0, 0)
    cell.text = "Fig.2 热图示例"
    cell.paragraphs[0].add_run().add_picture(str(image_path))
    doc.save(docx_path)

    result = module.extract_docx(docx_path, out_dir)

    assert len(result["figures"]) == 1
    figure = result["figures"][0]
    assert figure["figure_type"] == "heatmap"
    assert figure["is_reference_only"] is True
    assert Path(figure["extracted_path"]).is_relative_to(out_dir)
    assert "Fig.2 热图示例" in figure["current_text"]


def test_cli_writes_json_and_markdown_summary(tmp_path):
    module = load_module()
    docx_path = tmp_path / "sample.docx"
    out_dir = tmp_path / "out"
    build_sample_docx(docx_path)

    exit_code = module.main([str(docx_path), "--out-dir", str(out_dir)])

    assert exit_code == 0
    json_path = out_dir / "outline.json"
    markdown_path = out_dir / "outline.md"
    assert json_path.exists()
    assert markdown_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["project_id"] == "project-test-0001转录组诊断"
    assert "## Detected Modules" in markdown_path.read_text(encoding="utf-8")


def test_relationship_target_resolution_handles_package_absolute_paths():
    module = load_module()

    assert module._resolve_relationship_target("/word/media/image1.png") == "word/media/image1.png"
    assert module._resolve_relationship_target("media/image1.png") == "word/media/image1.png"
    assert module._resolve_relationship_target("../media/image1.png") is None
    assert module._resolve_relationship_target("/../media/image1.png") is None
    assert module._resolve_relationship_target("https://example.com/image.png") is None
    assert module._resolve_relationship_target("image.png", "External") is None


def test_extract_docx_wraps_invalid_package_errors(tmp_path):
    module = load_module()
    bad_docx = tmp_path / "bad.docx"
    bad_docx.write_text("not a docx", encoding="utf-8")

    with pytest.raises(module.DocxParseError):
        module.extract_docx(bad_docx, tmp_path / "out")


def test_extract_docx_wraps_missing_document_xml_errors(tmp_path):
    module = load_module()
    bad_docx = tmp_path / "missing-document.docx"
    with zipfile.ZipFile(bad_docx, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")

    with pytest.raises(module.DocxParseError):
        module.extract_docx(bad_docx, tmp_path / "out")
