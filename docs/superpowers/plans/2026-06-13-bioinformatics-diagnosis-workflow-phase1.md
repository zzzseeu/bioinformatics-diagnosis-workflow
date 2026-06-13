# Bioinformatics Diagnosis Workflow Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the current proposal parser skill into a staged bioinformatics diagnosis workflow skill with DOCX-dependent parsing, manifest/memory outputs, template-based code generation scaffolding, and report-template-aware report preparation.

**Architecture:** Keep one user-facing skill entrypoint, `bioinformatics-diagnosis-workflow`, and split implementation support across focused scripts, references, assets, and code templates. Preserve the existing DOCX outline extraction logic as the parsing core, then add small deterministic helpers for CSV manifests, project memory, result scanning, and report input preparation. Phase 1 builds a working framework and representative templates; broad analysis template coverage is deferred to a follow-up plan.

**Tech Stack:** Python standard library, pytest, existing `python-docx`-compatible fixtures, DOCX OOXML fallback, Markdown, CSV, R script templates, installed `docx` skill conventions.

---

## Scope Check

The approved design covers several subsystems. This plan intentionally implements Phase 1 only:

- rename skill and metadata
- add report template asset
- add reference contracts
- keep and move existing DOCX extraction
- add manifest, memory, result-scan, and report-input helper scripts
- add representative code templates
- add tests for script behavior and template/report rules

Do not implement full single-cell/bulk/ML analysis execution coverage in this plan. Add only representative templates that prove the pattern.

## File Structure

- Move/rename: `/Users/seeu/Desktop/Project/bioinfo-skills/docx-analysis-plan-parser/` to `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/`
  - This is the source skill repository. Keep git history by using `git mv` for tracked files where practical.
- Modify: `SKILL.md`
  - New metadata name/description and staged workflow instructions.
- Modify: `agents/openai.yaml`
  - Chinese display name and new default prompt.
- Create: `assets/报告格式模板-20250929.docx`
  - Copy from `/Users/seeu/Desktop/Project/报告格式模板-20250929.docx`.
- Modify/Create references:
  - `references/workflow-stages.md`: stage definitions and pause rules.
  - `references/manifest-schema.md`: CSV fields, statuses, execution modes.
  - `references/module-library.md`: keep current module SOPs and add execution-mode hints.
  - `references/report-template-map.md`: report sections, naming, image insertion rules.
  - `references/report-qc-rules.md`: report quality checklist.
  - `references/docx-patterns.md`: preserve existing DOCX extraction cues.
  - `references/output-schema.md`: replace old plan-only schema with staged output guidance, or remove only if no longer referenced.
- Move/modify: `scripts/extract_docx_outline.py`
  - Keep existing behavior. Do not add new fields in Phase 1 unless a task in this plan introduces a failing test for that field.
- Create: `scripts/build_manifest.py`
  - Read/write module-level CSV manifests with fixed schema.
- Create: `scripts/update_project_memory.py`
  - Create/update `workflow/PROJECT_MEMORY.md`.
- Create: `scripts/scan_project_results.py`
  - Scan result directories for PNG/PDF/CSV/XLSX/RDS/scripts and produce report manifest rows.
- Create: `scripts/prepare_report_inputs.py`
  - Build report input notes and validate PNG-only Word insertion candidates.
- Create templates:
  - `templates/code/bulk_de_analysis.R`
  - `templates/code/enrichment_clusterprofiler.R`
  - `templates/code/single_cell_qc_seurat.R`
- Modify tests:
  - Keep existing extraction tests.
  - Add `tests/test_manifest_and_memory.py`
  - Add `tests/test_result_scan_and_report_inputs.py`
  - Add `tests/test_skill_contract_files.py`

## Task 1: Rename Skill Metadata and Preserve DOCX Parser Contract

**Files:**
- Modify: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/SKILL.md`
- Modify: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/agents/openai.yaml`
- Test: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/tests/test_skill_contract_files.py`

- [ ] **Step 1: Rename repository directory**

Run:

```bash
cd /Users/seeu/Desktop/Project/bioinfo-skills
mv docx-analysis-plan-parser bioinformatics-diagnosis-workflow
cd bioinformatics-diagnosis-workflow
git status -sb
```

Expected: repository remains accessible; tracked files appear as moved/modified only after edits.

- [ ] **Step 2: Write failing contract tests**

Create `tests/test_skill_contract_files.py`:

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_skill_metadata_uses_new_name_only():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "name: bioinformatics-diagnosis-workflow" in text
    assert "生物信息诊断工作流" in text
    assert "docx-analysis-plan-parser" not in text


def test_skill_declares_docx_dependency_and_stage_pauses():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "docx" in text
    assert "每个阶段完成后暂停" in text
    assert "manifest.csv" in text
    assert "PROJECT_MEMORY.md" in text


def test_openai_yaml_matches_new_skill():
    text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert "生物信息诊断工作流" in text
    assert "bioinformatics-diagnosis-workflow" in text
```

- [ ] **Step 3: Run test to verify it fails**

Run:

```bash
python3 -m pytest tests/test_skill_contract_files.py -q
```

Expected: FAIL because old skill metadata still references the old name and lacks the new contract.

- [ ] **Step 4: Update `SKILL.md` minimally**

Replace `SKILL.md` with:

```markdown
---
name: bioinformatics-diagnosis-workflow
description: Use when Codex needs to run a staged bioinformatics diagnosis or mechanism workflow from Word方案文档 through requirements extraction, data/result matching, analysis planning, project code generation, manual task handoff, Word report generation, and report QC for single-cell, transcriptome, bulk, multi-omics, or client self-sequenced projects.
---

# 生物信息诊断工作流

Use this skill for diagnosis/mechanism bioinformatics projects that start from a Word `.docx` proposal and need staged analysis planning, project code generation, result review, and Word report generation.

## Required Dependency

- Also use the installed `docx` skill for every `.docx` operation, including proposal parsing, report template reading, and report writing.
- Treat Word proposal documents as the source of truth.
- Embedded Word images in proposals are reference/example figures unless the text explicitly says they are real results.

## Core Rules

- Default to staged execution. 每个阶段完成后暂停，等待用户确认再继续。
- Use Markdown plus `manifest.csv` outputs as user-facing artifacts; JSON is not a primary deliverable.
- Create and update `workflow/PROJECT_MEMORY.md` for each project.
- Generate project-specific code from templates when possible.
- For large single-cell or long-running tasks, run only temporary smoke tests, delete temporary test data/logs, and hand off full execution to the user.
- Do not keep temporary smoke-test data, logs, or pass/fail records in the project directory.
- Final report filenames must use `report/<项目编号>_<YYYYMMDD>_report.docx`, with `_v2`, `_v3`, etc. to avoid overwrites.
- Word reports insert PNG images only. Image order is image, image name, caption; all centered; image name is bold and light blue.

## Workflow

1. Parse proposal DOCX with the `docx` skill and `scripts/extract_docx_outline.py`.
2. Write `workflow/01_requirements.md` and `workflow/01_requirements_manifest.csv`; pause.
3. Check requirements against provided data/result directories; write `02_gap_check.*`; pause.
4. Generate `03_analysis_plan.md` and `03_analysis_manifest.csv`; pause.
5. Generate project code from `templates/code/`; run only safe automatic analyses or smoke tests; write `04_generated_code.md` and `04_code_manifest.csv`; pause.
6. Write manual execution handoff files for long-running or non-code-stable modules; pause.
7. Scan results and prepare report inputs; pause.
8. Generate Word report using `assets/报告格式模板-20250929.docx` and the `docx` skill; pause.
9. Run report QC and write `workflow/07_report_qc.md`.

## References

- Stage rules: `references/workflow-stages.md`
- Manifest schema: `references/manifest-schema.md`
- Module library: `references/module-library.md`
- DOCX extraction cues: `references/docx-patterns.md`
- Report template mapping: `references/report-template-map.md`
- Report QC: `references/report-qc-rules.md`

## Parser Command

```bash
python scripts/extract_docx_outline.py /path/to/input.docx --out-dir workflow/_docx_outline
```
```

- [ ] **Step 5: Update `agents/openai.yaml`**

Replace with:

```yaml
interface:
  display_name: "生物信息诊断工作流"
  short_description: "分阶段解析生信方案、生成分析计划、项目代码、人工任务和 Word 报告"
  brand_color: "#2E7D6E"
  default_prompt: "使用 $bioinformatics-diagnosis-workflow 解析生信项目方案 Word 文档，分阶段生成需求、manifest、分析计划、项目代码、人工任务、报告和质检结果。"

policy:
  allow_implicit_invocation: true
```

- [ ] **Step 6: Run test to verify it passes**

Run:

```bash
python3 -m pytest tests/test_skill_contract_files.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add SKILL.md agents/openai.yaml tests/test_skill_contract_files.py
git commit -m "rename skill to bioinformatics diagnosis workflow"
```

## Task 2: Add Report Template Asset and Reference Contracts

**Files:**
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/assets/报告格式模板-20250929.docx`
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/references/workflow-stages.md`
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/references/manifest-schema.md`
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/references/report-template-map.md`
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/references/report-qc-rules.md`
- Modify: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/references/module-library.md`
- Test: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/tests/test_skill_contract_files.py`

- [ ] **Step 1: Extend failing contract tests**

Append to `tests/test_skill_contract_files.py`:

```python
def test_report_template_asset_exists():
    asset = ROOT / "assets" / "报告格式模板-20250929.docx"

    assert asset.exists()
    assert asset.stat().st_size > 50_000


def test_reference_contracts_exist_and_include_required_rules():
    required = {
        "workflow-stages.md": ["默认暂停", "01_requirements", "07_report_qc"],
        "manifest-schema.md": ["module_id", "execution_mode", "smoke_test_then_manual"],
        "report-template-map.md": ["<项目编号>_<YYYYMMDD>_report.docx", "只插 PNG", "浅蓝色"],
        "report-qc-rules.md": ["示例图", "虚构", "PNG"],
    }
    for filename, terms in required.items():
        text = (ROOT / "references" / filename).read_text(encoding="utf-8")
        for term in terms:
            assert term in text
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m pytest tests/test_skill_contract_files.py::test_report_template_asset_exists tests/test_skill_contract_files.py::test_reference_contracts_exist_and_include_required_rules -q
```

Expected: FAIL because assets and references are missing.

- [ ] **Step 3: Copy report template asset**

Run:

```bash
mkdir -p assets
cp /Users/seeu/Desktop/Project/报告格式模板-20250929.docx assets/报告格式模板-20250929.docx
```

- [ ] **Step 4: Create `references/workflow-stages.md`**

```markdown
# Workflow Stages

默认每个阶段完成后暂停，等待用户确认后继续。

## Stage Outputs

| Stage | Markdown | Manifest |
| --- | --- | --- |
| 01_requirements | workflow/01_requirements.md | workflow/01_requirements_manifest.csv |
| 02_gap_check | workflow/02_gap_check.md | workflow/02_gap_check_manifest.csv |
| 03_analysis_plan | workflow/03_analysis_plan.md | workflow/03_analysis_manifest.csv |
| 04_generated_code | workflow/04_generated_code.md | workflow/04_code_manifest.csv |
| 05_manual_tasks | workflow/05_manual_tasks.md | workflow/05_manual_manifest.csv |
| 06_report_inputs | workflow/06_report_inputs.md | workflow/06_report_manifest.csv |
| 07_report_qc | workflow/07_report_qc.md | none |

## Pause Rule

After writing each stage output, summarize paths, blockers, and the recommended next stage. Do not continue until the user confirms.

## Clean Project Rule

Temporary smoke-test data, logs, and pass/fail records must be deleted before returning control to the user.
```

- [ ] **Step 5: Create `references/manifest-schema.md`**

```markdown
# Manifest Schema

User-facing manifests are CSV files. JSON is not a primary deliverable.

## Columns

stage,module_id,module_name,source_requirement,input_required,input_found,output_expected,output_found,execution_mode,code_template,generated_script,status,manual_action,report_section,notes

## Status Values

- pending
- ready
- auto_runnable
- smoke_test_passed
- manual_required
- completed
- blocked
- skipped

## Execution Modes

- auto
- smoke_test_then_manual
- manual
- report_only
- not_applicable
```

- [ ] **Step 6: Create `references/report-template-map.md`**

```markdown
# Report Template Map

Template asset: `assets/报告格式模板-20250929.docx`

## Output Naming

Default report path: `report/<项目编号>_<YYYYMMDD>_report.docx`.
If the file exists, append `_v2`, `_v3`, and so on.

## Section Sources

- Sections before `2 分析结果`: copy or normalize from proposal DOCX.
- `2 分析结果`: write from real project results only.
- `3 项目总结`: summarize actual completed results.
- `4 项目调整`: document deviations from the proposal.
- `5 软件列表`: derive from scripts, manifests, packages, and databases.
- `6 报告质检`: copy from proposal when present; otherwise use report QC rules and state the source.
- `参考文献`: combine proposal references and actual analysis/tool references.

## Word Image Rules

- Word reports only insert PNG images.
- Image block order: image, image name, figure caption.
- Image, image name, and caption are centered.
- Image name uses bold font and light blue color.
- Captions are centered and not bold by default.
- PDF figures are kept as deliverable files, not inserted into Word.
```

- [ ] **Step 7: Create `references/report-qc-rules.md`**

```markdown
# Report QC Rules

Check these before considering a Word report complete:

- Required template sections are present.
- Proposal-required modules are covered in analysis results or project adjustments.
- Word report inserts PNG images only.
- Image block order is image, image name, caption.
- Image, image name, and caption are centered.
- Image name is bold and light blue.
- All referenced figure/table files exist.
- Software list covers actual scripts, R packages, Python packages, tools, and databases.
- References cover proposal literature and actual analysis tools.
- Proposal example images are not treated as real results.
- No genes, datasets, sample sizes, or conclusions are invented.
- Project ID, disease, species, data source, and grouping match the proposal or are explained in project adjustments.
```

- [ ] **Step 8: Update `references/module-library.md` minimally**

Add this section near the top:

```markdown
## Execution Mode Hints

- Bulk/table analyses can be `auto` when inputs are small and complete.
- Single-cell and long-running analyses default to `smoke_test_then_manual`.
- GUI, online database, or Cytoscape-heavy steps default to `manual`.
- Report-only sections use `report_only`.
```

- [ ] **Step 9: Run tests**

```bash
python3 -m pytest tests/test_skill_contract_files.py -q
```

Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add assets references tests/test_skill_contract_files.py
git commit -m "add workflow references and report template asset"
```

## Task 3: Implement Manifest CSV Helper

**Files:**
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/scripts/build_manifest.py`
- Test: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/tests/test_manifest_and_memory.py`

- [ ] **Step 1: Write failing manifest tests**

Create `tests/test_manifest_and_memory.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_manifest_and_memory.py::test_build_manifest_writes_fixed_columns tests/test_manifest_and_memory.py::test_build_manifest_rejects_unknown_status -q
```

Expected: FAIL because `scripts/build_manifest.py` does not exist.

- [ ] **Step 3: Implement `scripts/build_manifest.py`**

```python
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
```

- [ ] **Step 4: Run tests**

```bash
python3 -m pytest tests/test_manifest_and_memory.py -q
```

Expected: PASS for manifest tests; memory tests are not added yet.

- [ ] **Step 5: Commit**

```bash
git add scripts/build_manifest.py tests/test_manifest_and_memory.py
git commit -m "add workflow manifest helper"
```

## Task 4: Implement Project Memory Helper

**Files:**
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/scripts/update_project_memory.py`
- Modify: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/tests/test_manifest_and_memory.py`

- [ ] **Step 1: Add failing memory tests**

Append:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_manifest_and_memory.py::test_update_project_memory_creates_state_summary -q
```

Expected: FAIL because `scripts/update_project_memory.py` does not exist.

- [ ] **Step 3: Implement `scripts/update_project_memory.py`**

```python
#!/usr/bin/env python3
"""Create PROJECT_MEMORY.md for staged bioinformatics projects."""

from __future__ import annotations

from pathlib import Path


def _table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
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
        [item.get("stage", ""), item.get("status", ""), item.get("artifact", ""), item.get("question", "")]
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
```

- [ ] **Step 4: Run tests**

```bash
python3 -m pytest tests/test_manifest_and_memory.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/update_project_memory.py tests/test_manifest_and_memory.py
git commit -m "add project memory helper"
```

## Task 5: Implement Result Scanner and Report Input Preparation

**Files:**
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/scripts/scan_project_results.py`
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/scripts/prepare_report_inputs.py`
- Test: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/tests/test_result_scan_and_report_inputs.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_result_scan_and_report_inputs.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_result_scan_and_report_inputs.py -q
```

Expected: FAIL because scripts do not exist.

- [ ] **Step 3: Implement `scripts/scan_project_results.py`**

```python
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
```

- [ ] **Step 4: Implement `scripts/prepare_report_inputs.py`**

```python
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
```

- [ ] **Step 5: Run tests**

```bash
python3 -m pytest tests/test_result_scan_and_report_inputs.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/scan_project_results.py scripts/prepare_report_inputs.py tests/test_result_scan_and_report_inputs.py
git commit -m "add result scan and report input helpers"
```

## Task 6: Add Representative Code Templates

**Files:**
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/templates/code/bulk_de_analysis.R`
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/templates/code/enrichment_clusterprofiler.R`
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/templates/code/single_cell_qc_seurat.R`
- Test: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/tests/test_skill_contract_files.py`

- [ ] **Step 1: Add failing template contract test**

Append:

```python
def test_representative_code_templates_exist():
    templates = {
        "bulk_de_analysis.R": ["{{EXPRESSION_MATRIX}}", "{{GROUP_METADATA}}", "{{OUTPUT_DIR}}"],
        "enrichment_clusterprofiler.R": ["{{GENE_LIST}}", "{{ORG_DB}}", "{{OUTPUT_DIR}}"],
        "single_cell_qc_seurat.R": ["{{INPUT_10X_DIR}}", "{{PROJECT_ID}}", "{{OUTPUT_DIR}}"],
    }
    for filename, tokens in templates.items():
        text = (ROOT / "templates" / "code" / filename).read_text(encoding="utf-8")
        for token in tokens:
            assert token in text
        assert "Times New Roman" in text
        assert "pdf" in text.lower()
        assert "png" in text.lower()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_skill_contract_files.py::test_representative_code_templates_exist -q
```

Expected: FAIL because templates do not exist.

- [ ] **Step 3: Create `templates/code/bulk_de_analysis.R`**

```r
suppressPackageStartupMessages({
  library(limma)
  library(ggplot2)
  library(pheatmap)
})

expression_matrix <- "{{EXPRESSION_MATRIX}}"
group_metadata <- "{{GROUP_METADATA}}"
group_column <- "{{GROUP_COLUMN}}"
case_label <- "{{CASE_LABEL}}"
control_label <- "{{CONTROL_LABEL}}"
output_dir <- "{{OUTPUT_DIR}}"

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
expr <- read.csv(expression_matrix, row.names = 1, check.names = FALSE)
meta <- read.csv(group_metadata, check.names = FALSE)
stopifnot("sample" %in% colnames(meta))
stopifnot(group_column %in% colnames(meta))
expr <- expr[, meta$sample, drop = FALSE]
design <- model.matrix(~ 0 + factor(meta[[group_column]], levels = c(control_label, case_label)))
colnames(design) <- c("control", "case")
fit <- lmFit(expr, design)
contrast <- makeContrasts(case - control, levels = design)
fit2 <- eBayes(contrasts.fit(fit, contrast))
deg <- topTable(fit2, number = Inf, adjust.method = "BH")
write.csv(deg, file.path(output_dir, "DEG_results.csv"))

deg$gene <- rownames(deg)
deg$significant <- deg$adj.P.Val < 0.05 & abs(deg$logFC) > 0.5
p <- ggplot(deg, aes(logFC, -log10(adj.P.Val), color = significant)) +
  geom_point(size = 1) +
  theme_bw(base_family = "Times New Roman")
ggsave(file.path(output_dir, "DEG_volcano.png"), p, width = 7, height = 5, dpi = 300)
ggsave(file.path(output_dir, "DEG_volcano.pdf"), p, width = 7, height = 5)

top_genes <- head(rownames(deg), 30)
png(file.path(output_dir, "DEG_top_heatmap.png"), width = 1800, height = 1600, res = 300)
pheatmap(expr[top_genes, , drop = FALSE], fontsize = 8, family = "Times New Roman")
dev.off()
pdf(file.path(output_dir, "DEG_top_heatmap.pdf"), width = 7, height = 6, family = "Times")
pheatmap(expr[top_genes, , drop = FALSE], fontsize = 8)
dev.off()
```

- [ ] **Step 4: Create `templates/code/enrichment_clusterprofiler.R`**

```r
suppressPackageStartupMessages({
  library(clusterProfiler)
  library(ggplot2)
  library({{ORG_DB}})
})

gene_list <- "{{GENE_LIST}}"
output_dir <- "{{OUTPUT_DIR}}"
org_db_name <- "{{ORG_DB}}"
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
genes <- scan(gene_list, what = character(), quiet = TRUE)
ego <- enrichGO(gene = genes, OrgDb = get(org_db_name), keyType = "{{KEY_TYPE}}", ont = "BP", pAdjustMethod = "BH")
write.csv(as.data.frame(ego), file.path(output_dir, "GO_BP_enrichment.csv"), row.names = FALSE)
p <- dotplot(ego, showCategory = 10) + theme(text = element_text(family = "Times New Roman"))
ggsave(file.path(output_dir, "GO_BP_dotplot.png"), p, width = 7, height = 5, dpi = 300)
ggsave(file.path(output_dir, "GO_BP_dotplot.pdf"), p, width = 7, height = 5)
```

- [ ] **Step 5: Create `templates/code/single_cell_qc_seurat.R`**

```r
suppressPackageStartupMessages({
  library(Seurat)
  library(ggplot2)
})

input_10x_dir <- "{{INPUT_10X_DIR}}"
project_id <- "{{PROJECT_ID}}"
output_dir <- "{{OUTPUT_DIR}}"
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
counts <- Read10X(input_10x_dir)
obj <- CreateSeuratObject(counts = counts, project = project_id, min.cells = 3, min.features = 200)
obj[["percent.mt"]] <- PercentageFeatureSet(obj, pattern = "^MT-|^mt-")
qc_plot <- VlnPlot(obj, features = c("nFeature_RNA", "nCount_RNA", "percent.mt"), ncol = 3) +
  theme(text = element_text(family = "Times New Roman"))
ggsave(file.path(output_dir, "sc_qc_violin.png"), qc_plot, width = 9, height = 4, dpi = 300)
ggsave(file.path(output_dir, "sc_qc_violin.pdf"), qc_plot, width = 9, height = 4)
obj <- subset(obj, subset = nFeature_RNA > {{MIN_FEATURES}} & nFeature_RNA < {{MAX_FEATURES}} & percent.mt < {{MAX_PERCENT_MT}})
obj <- NormalizeData(obj)
obj <- FindVariableFeatures(obj, selection.method = "vst", nfeatures = 3000)
saveRDS(obj, file.path(output_dir, "seurat_qc_normalized.rds"))
```

- [ ] **Step 6: Run tests**

```bash
python3 -m pytest tests/test_skill_contract_files.py::test_representative_code_templates_exist -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add templates/code tests/test_skill_contract_files.py
git commit -m "add representative analysis code templates"
```

## Task 7: Add Report Naming and PNG Rule Tests

**Files:**
- Modify: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/tests/test_result_scan_and_report_inputs.py`
- Modify: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/scripts/prepare_report_inputs.py`

- [ ] **Step 1: Add failing report path versioning test**

Append:

```python
def test_next_report_path_adds_version_when_report_exists(tmp_path):
    report = load_script("prepare_report_inputs.py")
    report_dir = tmp_path / "report"
    report_dir.mkdir()
    first = report_dir / "project-1178_20260613_report.docx"
    second = report_dir / "project-1178_20260613_report_v2.docx"
    first.write_bytes(b"docx")

    assert report.next_report_path(report_dir, "project-1178", "20260613") == second
```

- [ ] **Step 2: Run test**

```bash
python3 -m pytest tests/test_result_scan_and_report_inputs.py::test_next_report_path_adds_version_when_report_exists -q
```

Expected: PASS because Task 5 defines `next_report_path`.

- [ ] **Step 3: Verify `next_report_path` implementation**

Ensure `scripts/prepare_report_inputs.py` contains:

```python
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
```

- [ ] **Step 4: Run full report input tests**

```bash
python3 -m pytest tests/test_result_scan_and_report_inputs.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit the added report naming test**

```bash
git add tests/test_result_scan_and_report_inputs.py
git commit -m "test report naming rules"
```

## Task 8: Preserve Existing DOCX Extraction Tests After Rename

**Files:**
- Modify: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/tests/test_extract_docx_outline.py`
- Modify: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/scripts/extract_docx_outline.py` only if Step 1 fails because the script still refers to an old path or old skill name.

- [ ] **Step 1: Run existing extraction tests**

```bash
python3 -m pytest tests/test_extract_docx_outline.py -q
```

Expected: PASS. If pytest is unavailable in local environment, use the bundled Python environment or install pytest before execution.

- [ ] **Step 2: If tests fail due to old paths, update `SCRIPT_PATH`**

Ensure test uses:

```python
SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "extract_docx_outline.py"
```

- [ ] **Step 3: Add no-old-name assertion to extraction outputs if relevant**

Do not alter extraction result schema unless needed. If adding a field for workflow compatibility, include:

```python
assert result["image_rule"] == "Embedded Word images are reference figure types only, not real analysis results."
```

- [ ] **Step 4: Run tests again**

```bash
python3 -m pytest tests/test_extract_docx_outline.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit if changes were needed**

```bash
git add scripts/extract_docx_outline.py tests/test_extract_docx_outline.py
git commit -m "preserve docx extraction after workflow rename"
```

If no files changed, do not create a commit.

## Task 9: End-to-End Phase 1 Smoke Fixture

**Files:**
- Create: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/tests/test_phase1_workflow_contract.py`
- Uses existing scripts.

- [ ] **Step 1: Write failing end-to-end contract test**

Create `tests/test_phase1_workflow_contract.py`:

```python
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
    (results / "Figure1.png").write_bytes(b"png")
    (results / "Figure1.pdf").write_bytes(b"pdf")

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
    report_blocks = report.build_image_blocks(
        [{"path": row["output_found"], "name": "Figure 1", "caption": "UMAP"} for row in scan_rows]
    )
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
    assert (workflow / "PROJECT_MEMORY.md").exists()
    assert report.next_report_path(report_dir, "project-1178", "20260613").name == "project-1178_20260613_report.docx"
```

- [ ] **Step 2: Run test to verify behavior**

```bash
python3 -m pytest tests/test_phase1_workflow_contract.py -q
```

Expected: PASS if prior tasks are complete.

- [ ] **Step 3: Run all tests**

```bash
python3 -m pytest tests -q
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_phase1_workflow_contract.py
git commit -m "add phase one workflow contract test"
```

## Task 10: Final Validation and Install Sync

**Files:**
- Source repo: `/Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow`
- Installed skill target: `/Users/seeu/.codex/skills/bioinformatics-diagnosis-workflow`

- [ ] **Step 1: Run test suite**

```bash
cd /Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow
python3 -m pytest tests -q
```

Expected: PASS.

- [ ] **Step 2: Validate report template asset is tracked**

```bash
test -f assets/报告格式模板-20250929.docx
git status -sb
```

Expected: clean working tree after all commits.

- [ ] **Step 3: Sync installed skill copy**

Run:

```bash
rm -rf /Users/seeu/.codex/skills/bioinformatics-diagnosis-workflow
mkdir -p /Users/seeu/.codex/skills/bioinformatics-diagnosis-workflow
rsync -a --exclude .git /Users/seeu/Desktop/Project/bioinfo-skills/bioinformatics-diagnosis-workflow/ /Users/seeu/.codex/skills/bioinformatics-diagnosis-workflow/
```

If keeping the old installed skill would cause confusion, remove it after confirming the new skill works:

```bash
rm -rf /Users/seeu/.codex/skills/docx-analysis-plan-parser
```

- [ ] **Step 4: Commit any final source changes**

Only if files changed after previous commits:

```bash
git status -sb
git add .
git commit -m "finalize bioinformatics diagnosis workflow phase one"
```

- [ ] **Step 5: Push branch**

```bash
git push -u origin HEAD
```

Expected: remote branch updated.

## Self-Review

Spec coverage:

- New name and no old-name compatibility: Task 1.
- `docx` dependency: Task 1 and reference contracts.
- Report template asset: Task 2.
- Markdown plus CSV manifests: Task 3 and references.
- PROJECT_MEMORY: Task 4.
- Code templates: Task 6.
- Safe execution/smoke-test handoff rules: references in Task 2 and template contract in Task 6.
- Report naming and PNG-only insertion rules: Task 2, Task 5, Task 7.
- Report QC rules: Task 2.
- Existing DOCX parser preservation: Task 8.
- End-to-end Phase 1 sanity: Task 9.

Deferred by design:

- Full code template library for all modules.
- Fully automated Word report writing implementation beyond report-input preparation and contract rules.
- Full large single-cell execution automation.

Placeholder scan:

- No placeholder markers remain.
- Conditional repair steps include exact failure conditions and exact commands.

Type/name consistency:

- Manifest columns match `MANIFEST_COLUMNS`.
- Execution modes and statuses match approved schema.
- Report naming uses `<project_id>_<YYYYMMDD>_report.docx`.
