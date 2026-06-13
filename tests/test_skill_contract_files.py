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
