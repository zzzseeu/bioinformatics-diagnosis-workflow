# DOCX Patterns

## Common Sections
- 背景
- 方法
- 研究目标
- 拟解决的关键科学问题
- 创新性或项目亮点
- 流程图
- 数据分析
- 数据准备
- 分析结果梳理参考
- 临床意义
- 参考文献

These sections are common patterns, not required sections. The actual Word document controls the output.

## Extraction Cues
- `项目编号：` usually identifies the job or project ID.
- `GSE\d+` identifies GEO datasets.
- `PMID`, `PMIDs`, `PMID:`, and `PMID：` identify literature evidence.
- Bracketed notes such as `【注：...】` or `【备注：...】` often contain constraints or client questions and should be preserved in `需确认信息` when they affect execution.
- Captions beginning with `Fig.`, `Figure`, `图`, or `流程图` should be associated with nearby embedded images.

## Image Rule
All embedded Word images are reference/example figures unless the text explicitly says they are actual results. Use images to infer expected plot type only.

## New Pattern Maintenance
When a new Word document contains a reusable module or structure:
- add analysis SOPs to `module-library.md`;
- add wording, heading, caption, or extraction patterns here;
- update the script when reliable extraction needs deterministic code.
