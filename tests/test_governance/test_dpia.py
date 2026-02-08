"""Tests for DPIA auto-generation."""

from nss.governance.dpia import DPIAGenerator


def test_generate_produces_all_sections() -> None:
    gen = DPIAGenerator()
    report = gen.generate(
        processing_activity="LLM query processing",
        data_categories=["email", "name"],
        risk_tier=2,
    )
    assert len(report.sections) == 5
    assert "1_description" in report.sections
    assert "2_necessity" in report.sections
    assert "3_risk_assessment" in report.sections
    assert "4_mitigation" in report.sections
    assert "5_dpo_consultation" in report.sections


def test_risk_level_matches_tier() -> None:
    gen = DPIAGenerator()
    report = gen.generate("test", ["data"], risk_tier=0)
    assert report.risk_level == "CRITICAL"
    report = gen.generate("test", ["data"], risk_tier=3)
    assert report.risk_level == "LOW"


def test_dpo_required_for_high_risk() -> None:
    gen = DPIAGenerator()
    report = gen.generate("test", ["data"], risk_tier=0)
    assert report.sections["5_dpo_consultation"]["required"] is True
    assert report.recommendation == "REVIEW_REQUIRED"


def test_dpo_not_required_for_low_risk() -> None:
    gen = DPIAGenerator()
    report = gen.generate("test", ["data"], risk_tier=3)
    assert report.sections["5_dpo_consultation"]["required"] is False
    assert report.recommendation == "PROCEED"


def test_to_markdown_output() -> None:
    gen = DPIAGenerator()
    report = gen.generate("LLM processing", ["email"], risk_tier=2)
    md = gen.to_markdown(report)
    assert "# Data Protection Impact Assessment" in md
    assert report.report_id in md
    assert "MEDIUM" in md
