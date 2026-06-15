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
3. Check requirements against provided data/result directories; write `workflow/02_gap_check.md` and `workflow/02_gap_check_manifest.csv`; pause.
4. Generate `workflow/03_analysis_plan.md` and `workflow/03_analysis_manifest.csv`; pause.
5. Generate project code from `templates/code/`; run only safe automatic analyses or smoke tests; write `workflow/04_generated_code.md` and `workflow/04_code_manifest.csv`; pause.
6. Write `workflow/05_manual_tasks.md` and `workflow/05_manual_manifest.csv` for long-running or non-code-stable modules; pause.
7. Scan results and prepare `workflow/06_report_inputs.md` and `workflow/06_report_manifest.csv`; pause.
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
