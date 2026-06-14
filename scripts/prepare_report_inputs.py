#!/usr/bin/env python3
"""Prepare report input structures from scanned project results."""

from __future__ import annotations

from pathlib import Path


def build_image_blocks(items: list[dict[str, str]]) -> list[dict[str, object]]:
    blocks = []
    for item in items:
        path = Path(item["path"])
        if path.suffix.lower() != ".png":
            continue
        blocks.append(
            {
                "path": str(path),
                "name": item.get("name", path.stem),
                "caption": item.get("caption", ""),
                "word_insertable": True,
            }
        )
    return blocks


def next_report_path(report_dir: str | Path, project_id: str, date_stamp: str) -> Path:
    directory = Path(report_dir)
    base = directory / f"{project_id}_{date_stamp}_report.docx"
    if not base.exists():
        return base
    counter = 2
    while True:
        candidate = directory / f"{project_id}_{date_stamp}_report_v{counter}.docx"
        if not candidate.exists():
            return candidate
        counter += 1
