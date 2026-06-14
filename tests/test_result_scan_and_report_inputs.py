import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PNG_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"


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
    png.write_bytes(PNG_BYTES)
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


def test_prepare_report_inputs_accepts_scanner_output_and_reports_pdf_png_gap(tmp_path):
    report = load_script("prepare_report_inputs.py")
    png = tmp_path / "Fig1.png"
    pdf = tmp_path / "Fig2.pdf"
    png.write_bytes(PNG_BYTES)
    pdf.write_bytes(b"pdf")
    rows = [
        {"output_found": str(png), "notes": "png_figure"},
        {"output_found": str(pdf), "notes": "pdf_attachment"},
    ]

    blocks = report.build_image_blocks(rows)
    issues = report.find_report_input_issues(rows)
    notes = report.build_report_notes(blocks, issues)

    assert blocks[0]["path"] == str(png)
    assert issues == [
        {
            "path": str(pdf),
            "issue": "missing_png_export",
            "action": f"Export PNG before Word insertion: {pdf.with_suffix('.png')}",
        }
    ]
    assert "## PNG Images For Word" in notes
    assert "missing_png_export" in notes


def test_prepare_report_inputs_rejects_invalid_png(tmp_path):
    report = load_script("prepare_report_inputs.py")
    bad_png = tmp_path / "bad.png"
    bad_png.write_bytes(b"not a png")

    try:
        report.build_image_blocks([{"path": str(bad_png)}])
    except ValueError as exc:
        assert "Invalid PNG image" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_next_report_path_adds_version_when_report_exists(tmp_path):
    report = load_script("prepare_report_inputs.py")
    report_dir = tmp_path / "report"
    report_dir.mkdir()
    first = report_dir / "project-1178_20260613_report.docx"
    second = report_dir / "project-1178_20260613_report_v2.docx"
    first.write_bytes(b"docx")

    assert report.next_report_path(report_dir, "project-1178", "20260613") == second


def test_next_report_path_rejects_unsafe_filename_parts(tmp_path):
    report = load_script("prepare_report_inputs.py")

    try:
        report.next_report_path(tmp_path, "../escape", "20260613")
    except ValueError as exc:
        assert "Unsafe project_id" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

    try:
        report.next_report_path(tmp_path, "project-1178", "2026/06/13")
    except ValueError as exc:
        assert "Unsafe date_stamp" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_scan_project_results_rejects_missing_roots(tmp_path):
    scanner = load_script("scan_project_results.py")

    try:
        scanner.scan_paths([tmp_path / "missing"])
    except FileNotFoundError as exc:
        assert "Scan root does not exist" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")
