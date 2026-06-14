#!/usr/bin/env python3
"""Scan project result directories into manifest-like rows."""

from __future__ import annotations

from pathlib import Path


def classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "png_figure"
    if suffix == ".pdf":
        return "pdf_attachment"
    if suffix in {".csv", ".tsv", ".xlsx", ".xls"}:
        return "table"
    if suffix in {".r", ".py", ".sh"}:
        return "script"
    if suffix in {".rds", ".rdata", ".h5ad"}:
        return "object"
    return "other"


def scan_paths(paths: list[str | Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for base in paths:
        root = Path(base)
        if not root.exists():
            continue
        for file_path in sorted(path for path in root.rglob("*") if path.is_file()):
            kind = classify(file_path)
            if kind == "other":
                continue
            rows.append(
                {
                    "stage": "06_report_inputs",
                    "module_id": "",
                    "module_name": "",
                    "source_requirement": "",
                    "input_required": "",
                    "input_found": "",
                    "output_expected": "",
                    "output_found": str(file_path),
                    "execution_mode": "report_only",
                    "code_template": "",
                    "generated_script": str(file_path) if kind == "script" else "",
                    "status": "completed",
                    "manual_action": "",
                    "report_section": "2 分析结果" if kind == "png_figure" else "",
                    "notes": kind,
                }
            )
    return rows
