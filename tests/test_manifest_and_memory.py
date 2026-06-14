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
