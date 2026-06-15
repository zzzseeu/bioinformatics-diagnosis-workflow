#!/usr/bin/env python3
"""Create PROJECT_MEMORY.md for staged bioinformatics projects."""

from __future__ import annotations

from pathlib import Path


def _cell(value: str) -> str:
    return str(value).replace("\n", "<br>").replace("|", "\\|")


def _table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(_cell(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(_cell(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def write_project_memory(
    path: str | Path,
    *,
    project: dict[str, str],
    stages: list[dict[str, str]],
    modules: list[dict[str, str]],
    decisions: list[str],
    blockers: list[str],
    paths: dict[str, str],
    handoff: str,
) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage_rows = [
        [
            item.get("stage", ""),
            item.get("status", ""),
            item.get("artifact", ""),
            item.get("question", ""),
        ]
        for item in stages
    ]
    module_rows = [
        [
            item.get("module", ""),
            item.get("execution_mode", ""),
            item.get("input_status", ""),
            item.get("code_status", ""),
            item.get("result_status", ""),
            item.get("report_status", ""),
        ]
        for item in modules
    ]
    lines = [
        "# PROJECT_MEMORY",
        "",
        "## 项目基本信息",
        f"- 项目编号：{project.get('project_id', '')}",
        f"- 项目主题：{project.get('title', '')}",
        f"- 疾病/表型：{project.get('disease', '')}",
        f"- 物种：{project.get('species', '')}",
        f"- 数据类型：{project.get('data_type', '')}",
        f"- 当前阶段：{project.get('current_stage', '')}",
        f"- 最近更新时间：{project.get('updated_at', '')}",
        "",
        "## 阶段状态",
        _table(["阶段", "状态", "关键产物", "待确认问题"], stage_rows),
        "",
        "## 分析模块状态",
        _table(["模块", "执行模式", "输入状态", "代码状态", "结果状态", "报告状态"], module_rows),
        "",
        "## 关键决策",
    ]
    lines.extend(f"- {item}" for item in decisions)
    lines.extend(["", "## 待办与阻塞"])
    lines.extend(f"- {item}" for item in blockers)
    lines.extend(
        [
            "",
            "## 结果目录约定",
            f"- 输入数据目录：{paths.get('input', '')}",
            f"- 代码目录：{paths.get('code', '')}",
            f"- 结果目录：{paths.get('result', '')}",
            f"- 报告目录：{paths.get('report', '')}",
            "",
            "## 交接摘要",
            handoff,
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")
