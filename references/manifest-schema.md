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
