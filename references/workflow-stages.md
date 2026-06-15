# Workflow Stages

默认暂停：每个阶段完成后暂停，等待用户确认后继续。

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
