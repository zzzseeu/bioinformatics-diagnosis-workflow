#!/usr/bin/env python3
"""Read and write bioinformatics workflow manifest CSV files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


MANIFEST_COLUMNS = [
    "stage",
    "module_id",
    "module_name",
    "source_requirement",
    "input_required",
    "input_found",
    "output_expected",
    "output_found",
    "execution_mode",
    "code_template",
    "generated_script",
    "status",
    "manual_action",
    "report_section",
    "notes",
]

STATUS_VALUES = {
    "pending",
    "ready",
    "auto_runnable",
    "smoke_test_passed",
    "manual_required",
    "completed",
    "blocked",
    "skipped",
}

EXECUTION_MODES = {
    "auto",
    "smoke_test_then_manual",
    "manual",
    "report_only",
    "not_applicable",
}


def normalize_row(row: dict[str, object]) -> dict[str, str]:
    normalized = {column: str(row.get(column, "") or "") for column in MANIFEST_COLUMNS}
    status = normalized["status"]
    mode = normalized["execution_mode"]
    if status and status not in STATUS_VALUES:
        raise ValueError(f"Unknown status: {status}")
    if mode and mode not in EXECUTION_MODES:
        raise ValueError(f"Unknown execution_mode: {mode}")
    return normalized


def write_manifest(path: str | Path, rows: list[dict[str, object]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(normalize_row(row))


def read_manifest(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a workflow manifest CSV.")
    parser.add_argument("manifest")
    args = parser.parse_args(argv)
    rows = read_manifest(args.manifest)
    for row in rows:
        normalize_row(row)
    print(f"validated {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
