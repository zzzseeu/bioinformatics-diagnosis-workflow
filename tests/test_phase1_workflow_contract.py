import csv
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


def test_phase1_helpers_create_clean_workflow_artifacts(tmp_path):
    manifest = load_script("build_manifest.py")
    memory = load_script("update_project_memory.py")
    scanner = load_script("scan_project_results.py")
    report = load_script("prepare_report_inputs.py")

    workflow = tmp_path / "workflow"
    results = tmp_path / "results"
    report_dir = tmp_path / "report"
    results.mkdir()
    report_dir.mkdir()
    (results / "Figure1.png").write_bytes(PNG_BYTES)
    (results / "Figure2.pdf").write_bytes(b"pdf")

    manifest_path = workflow / "03_analysis_manifest.csv"
    manifest.write_manifest(
        manifest_path,
        [
            {
                "stage": "03_analysis_plan",
                "module_id": "M01",
                "module_name": "单细胞质控",
                "execution_mode": "smoke_test_then_manual",
                "status": "manual_required",
                "report_section": "2 分析结果",
            }
        ],
    )
    scan_rows = scanner.scan_paths([results])
    report_items = [
        {"output_found": row["output_found"], "name": "Figure 1", "caption": "UMAP"} for row in scan_rows
    ]
    report_blocks = report.build_image_blocks(report_items)
    report_issues = report.find_report_input_issues(report_items)
    memory.write_project_memory(
        workflow / "PROJECT_MEMORY.md",
        project={
            "project_id": "project-1178",
            "title": "骨质疏松单细胞分析",
            "disease": "骨质疏松症",
            "species": "SD大鼠",
            "data_type": "scRNA-seq",
            "current_stage": "06_report_inputs",
            "updated_at": "2026-06-13",
        },
        stages=[],
        modules=[],
        decisions=[],
        blockers=[],
        paths={"input": "data/", "code": "scripts/", "result": "results/", "report": "report/"},
        handoff="等待报告生成。",
    )

    with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["execution_mode"] == "smoke_test_then_manual"
    assert len(report_blocks) == 1
    assert report_blocks[0]["path"].endswith("Figure1.png")
    assert report_issues[0]["issue"] == "missing_png_export"
    assert (workflow / "PROJECT_MEMORY.md").exists()
    assert report.next_report_path(report_dir, "project-1178", "20260613").name == (
        "project-1178_20260613_report.docx"
    )
