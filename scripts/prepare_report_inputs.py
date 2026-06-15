#!/usr/bin/env python3
"""Prepare report input structures from scanned project results."""

from __future__ import annotations

import re
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SAFE_FILENAME_PART = re.compile(r"^[A-Za-z0-9._-]+$")


def _path_from_item(item: dict[str, str]) -> Path:
    raw_path = item.get("path") or item.get("output_found")
    if not raw_path:
        raise ValueError("Report image item requires path or output_found")
    return Path(raw_path)


def _is_valid_png(path: Path) -> bool:
    if not path.is_file():
        return False
    with path.open("rb") as handle:
        return handle.read(len(PNG_SIGNATURE)) == PNG_SIGNATURE


def build_image_blocks(items: list[dict[str, str]]) -> list[dict[str, object]]:
    blocks = []
    for item in items:
        path = _path_from_item(item)
        if path.suffix.lower() != ".png":
            continue
        if not _is_valid_png(path):
            raise ValueError(f"Invalid PNG image: {path}")
        blocks.append(
            {
                "path": str(path),
                "name": item.get("name", path.stem),
                "caption": item.get("caption", ""),
                "word_insertable": True,
            }
        )
    return blocks


def find_report_input_issues(items: list[dict[str, str]]) -> list[dict[str, str]]:
    issues = []
    for item in items:
        path = _path_from_item(item)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            png_peer = path.with_suffix(".png")
            if not png_peer.exists():
                issues.append(
                    {
                        "path": str(path),
                        "issue": "missing_png_export",
                        "action": f"Export PNG before Word insertion: {png_peer}",
                    }
                )
        elif suffix == ".png" and not _is_valid_png(path):
            issues.append(
                {
                    "path": str(path),
                    "issue": "invalid_png",
                    "action": "Regenerate a valid PNG before Word insertion.",
                }
            )
    return issues


def build_report_notes(image_blocks: list[dict[str, object]], issues: list[dict[str, str]]) -> str:
    lines = [
        "# Report Inputs",
        "",
        "## PNG Images For Word",
    ]
    if image_blocks:
        lines.extend(f"- {item['name']}: {item['path']}" for item in image_blocks)
    else:
        lines.append("- None")
    lines.extend(["", "## Report Input Issues"])
    if issues:
        lines.extend(f"- {item['issue']}: {item['path']} -> {item['action']}" for item in issues)
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def next_report_path(report_dir: str | Path, project_id: str, date_stamp: str) -> Path:
    if not SAFE_FILENAME_PART.fullmatch(project_id):
        raise ValueError(f"Unsafe project_id for report filename: {project_id}")
    if not SAFE_FILENAME_PART.fullmatch(date_stamp):
        raise ValueError(f"Unsafe date_stamp for report filename: {date_stamp}")
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
