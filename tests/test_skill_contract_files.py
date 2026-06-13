from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_skill_metadata_uses_bioinformatics_diagnosis_workflow_name():
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "name: bioinformatics-diagnosis-workflow" in skill_text
    assert "生物信息诊断工作流" in skill_text
    assert "docx-analysis-plan-parser" not in skill_text


def test_skill_contract_declares_docx_dependency_and_staged_outputs():
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "docx" in skill_text
    assert "每个阶段完成后暂停" in skill_text
    assert "manifest.csv" in skill_text
    assert "PROJECT_MEMORY.md" in skill_text


def test_openai_agent_contract_uses_bioinformatics_diagnosis_workflow():
    agent_text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert "生物信息诊断工作流" in agent_text
    assert "bioinformatics-diagnosis-workflow" in agent_text


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
