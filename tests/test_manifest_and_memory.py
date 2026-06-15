import csv
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


def test_build_manifest_writes_fixed_columns(tmp_path):
    module = load_script("build_manifest.py")
    output = tmp_path / "manifest.csv"
    rows = [
        {
            "stage": "03_analysis_plan",
            "module_id": "M01",
            "module_name": "差异表达分析",
            "execution_mode": "auto",
            "status": "ready",
        }
    ]

    module.write_manifest(output, rows)

    with output.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == module.MANIFEST_COLUMNS
        loaded = list(reader)

    assert loaded[0]["module_id"] == "M01"
    assert loaded[0]["module_name"] == "差异表达分析"
    assert loaded[0]["input_required"] == ""


def test_build_manifest_rejects_unknown_status(tmp_path):
    module = load_script("build_manifest.py")

    try:
        module.write_manifest(tmp_path / "bad.csv", [{"status": "done"}])
    except ValueError as exc:
        assert "Unknown status" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_build_manifest_rejects_unknown_execution_mode(tmp_path):
    module = load_script("build_manifest.py")

    try:
        module.write_manifest(tmp_path / "bad.csv", [{"execution_mode": "cluster"}])
    except ValueError as exc:
        assert "Unknown execution_mode" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_build_manifest_rejects_malformed_header(tmp_path):
    module = load_script("build_manifest.py")
    bad_manifest = tmp_path / "bad.csv"
    bad_manifest.write_text("stage,module_id,extra\n03_analysis_plan,M01,value\n", encoding="utf-8")

    try:
        module.read_manifest(bad_manifest)
    except ValueError as exc:
        assert "Invalid manifest header" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_build_manifest_rejects_malformed_row_width(tmp_path):
    module = load_script("build_manifest.py")
    bad_manifest = tmp_path / "bad.csv"
    header = ",".join(module.MANIFEST_COLUMNS)
    row = ",".join(["value"] * (len(module.MANIFEST_COLUMNS) + 1))
    bad_manifest.write_text(f"{header}\n{row}\n", encoding="utf-8")

    try:
        module.read_manifest(bad_manifest)
    except ValueError as exc:
        assert "Invalid manifest row width" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_build_manifest_rejects_missing_row_cells(tmp_path):
    module = load_script("build_manifest.py")
    bad_manifest = tmp_path / "bad.csv"
    header = ",".join(module.MANIFEST_COLUMNS)
    bad_manifest.write_text(f"{header}\n03_analysis_plan,M01\n", encoding="utf-8")

    try:
        module.read_manifest(bad_manifest)
    except ValueError as exc:
        assert "Invalid manifest row width" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_build_manifest_main_returns_nonzero_for_user_input_errors(tmp_path, capsys):
    module = load_script("build_manifest.py")

    exit_code = module.main([str(tmp_path / "missing.csv")])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "error:" in captured.err


def test_update_project_memory_creates_state_summary(tmp_path):
    module = load_script("update_project_memory.py")
    memory = tmp_path / "workflow" / "PROJECT_MEMORY.md"

    module.write_project_memory(
        memory,
        project={
            "project_id": "project-1178",
            "title": "骨质疏松单细胞分析",
            "disease": "骨质疏松症",
            "species": "SD大鼠",
            "data_type": "scRNA-seq",
            "current_stage": "03_analysis_plan",
            "updated_at": "2026-06-13",
        },
        stages=[
            {
                "stage": "01_requirements",
                "status": "completed",
                "artifact": "workflow/01_requirements.md",
                "question": "",
            }
        ],
        modules=[
            {
                "module": "hdWGCNA",
                "execution_mode": "smoke_test_then_manual",
                "input_status": "ready",
                "code_status": "pending",
                "result_status": "pending",
                "report_status": "pending",
            }
        ],
        decisions=["2026-06-13：采用分阶段暂停确认。"],
        blockers=["等待客户确认关键细胞。"],
        paths={
            "input": "data/",
            "code": "scripts/",
            "result": "results/",
            "report": "report/",
        },
        handoff="下一步确认分析计划。",
    )

    text = memory.read_text(encoding="utf-8")
    assert "# PROJECT_MEMORY" in text
    assert "project-1178" in text
    assert "| 01_requirements | completed | workflow/01_requirements.md |  |" in text
    assert "| hdWGCNA | smoke_test_then_manual | ready | pending | pending | pending |" in text
    assert "等待客户确认关键细胞" in text


def test_update_project_memory_escapes_markdown_table_cells(tmp_path):
    module = load_script("update_project_memory.py")
    memory = tmp_path / "workflow" / "PROJECT_MEMORY.md"

    module.write_project_memory(
        memory,
        project={},
        stages=[
            {
                "stage": "01_requirements",
                "status": "completed",
                "artifact": "workflow/01_requirements.md",
                "question": "A | B?\n请确认",
            }
        ],
        modules=[],
        decisions=[],
        blockers=[],
        paths={},
        handoff="",
    )

    text = memory.read_text(encoding="utf-8")
    assert "A \\| B?<br>请确认" in text
