import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_scan_project_results_classifies_outputs(tmp_path):
    scanner = load_script("scan_project_results.py")
    (tmp_path / "results" / "figures").mkdir(parents=True)
    (tmp_path / "results" / "tables").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "results" / "figures" / "Fig1_umap.png").write_bytes(b"png")
    (tmp_path / "results" / "figures" / "Fig1_umap.pdf").write_bytes(b"pdf")
    (tmp_path / "results" / "tables" / "markers.csv").write_text("gene,p\nA,0.01\n", encoding="utf-8")
    (tmp_path / "scripts" / "single_cell_qc.R").write_text("library(Seurat)\n", encoding="utf-8")

    rows = scanner.scan_paths([tmp_path / "results", tmp_path / "scripts"])

    assert any(row["output_found"].endswith("Fig1_umap.png") and row["notes"] == "png_figure" for row in rows)
    assert any(row["output_found"].endswith("Fig1_umap.pdf") and row["notes"] == "pdf_attachment" for row in rows)
    assert any(row["output_found"].endswith("markers.csv") and row["notes"] == "table" for row in rows)
    assert any(row["output_found"].endswith("single_cell_qc.R") and row["notes"] == "script" for row in rows)


def test_prepare_report_inputs_accepts_png_and_rejects_pdf_for_word(tmp_path):
    report = load_script("prepare_report_inputs.py")
    png = tmp_path / "Fig1.png"
    pdf = tmp_path / "Fig1.pdf"
    png.write_bytes(b"png")
    pdf.write_bytes(b"pdf")

    blocks = report.build_image_blocks(
        [
            {"path": str(png), "name": "Figure 1. UMAP", "caption": "细胞注释结果。"},
            {"path": str(pdf), "name": "Figure 1 PDF", "caption": "PDF 附件。"},
        ]
    )

    assert blocks == [
        {"path": str(png), "name": "Figure 1. UMAP", "caption": "细胞注释结果。", "word_insertable": True}
    ]
