---
name: docx-analysis-plan-parser
description: Use when Codex needs to parse a bioinformatics project proposal Word document (`.docx`) and produce a complete SOP-level Chinese Markdown analysis plan. Trigger for requests involving Word方案解析, 项目方案docx, 转录组/单细胞/生信分析方案提取, extracting methods/data/figures from DOCX proposals, or updating this skill when new proposal analysis modules appear.
---

# DOCX Analysis Plan Parser

Parse bioinformatics proposal `.docx` files and generate a faithful, normalized, SOP-level Chinese Markdown analysis plan.

## Core Rules

- Treat the actual Word document as the source of truth.
- Preserve the source topic, disease, species, datasets, group design, methods, client notes, and requested modules.
- Do not invent datasets, genes, sample sizes, PMIDs, conclusions, or analysis results.
- Do not include standalone `总体技术路线` or `参考文献/PMID` sections by default.
- Do not hard-code a local environment name. Use any available environment or toolchain that can parse `.docx`; if none is available, ask the user which environment contains a DOCX parser.
- Embedded Word images are reference/example figures only. Do not infer real genes, values, trends, or conclusions from them.
- Every final analysis figure described in the plan should be exported as both PNG and PDF, with Times New Roman used for all plot text.

## Workflow

1. Confirm the user provided a `.docx` path or an accessible DOCX file.
2. Resolve `scripts/extract_docx_outline.py` relative to this skill directory and run it with a DOCX-capable environment.
3. Read the generated `outline.json` and `outline.md`.
4. Read `references/output-schema.md` before writing the final answer.
5. Read `references/module-library.md` for detected modules. For modules not covered there, preserve the source module and write a practical SOP from the source text.
6. Read `references/docx-patterns.md` when section structure, captions, image context, or extraction ambiguity matters.
7. Output Chinese Markdown following the schema.
8. Include `需确认信息` for conflicts, missing metadata, client notes, or ambiguous decisions.

## Parser Command

Use this pattern from the skill directory, replacing paths as needed:

```bash
python scripts/extract_docx_outline.py /path/to/input.docx --out-dir tmp/docx-analysis-plan/<document-stem>
```

If that Python cannot import `docx`, try another available DOCX-capable environment or toolchain. Ask the user which local environment has a DOCX parser only when no usable option is available.

## Maintenance

When a future Word document introduces a reusable new analysis point, method module, figure type, dataset pattern, or recurring client note:

- preserve it in the current generated plan;
- update `references/module-library.md` for new analysis modules or SOP patterns;
- update `references/docx-patterns.md` for document structure, wording, captions, or extraction cues;
- update `references/output-schema.md` only when the final Markdown contract changes;
- update `scripts/extract_docx_outline.py` when reliable extraction requires code;
- run quick validation and at least one representative extraction after updating.
