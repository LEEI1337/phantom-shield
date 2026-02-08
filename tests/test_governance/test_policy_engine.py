"""Tests for governance policy engine."""

from nss.governance.policy_engine import PolicyEngine


def test_admin_passes_all() -> None:
    engine = PolicyEngine()
    result = engine.evaluate({"role": "admin", "risk_tier": 0, "tool_name": "anything"})
    assert result.allowed is True
    assert len(result.violations) == 0


def test_viewer_blocked_high_risk() -> None:
    engine = PolicyEngine()
    result = engine.evaluate({"role": "viewer", "risk_tier": 1})
    assert result.allowed is False
    assert any("risk tier" in v.lower() for v in result.violations)


def test_pii_requires_privacy_tier() -> None:
    engine = PolicyEngine()
    result = engine.evaluate({"role": "admin", "pii_detected": True, "privacy_tier": 0})
    assert result.allowed is False
    assert any("pii" in v.lower() for v in result.violations)


def test_pii_with_sufficient_tier() -> None:
    engine = PolicyEngine()
    result = engine.evaluate({"role": "admin", "pii_detected": True, "privacy_tier": 1})
    assert result.allowed is True


def test_tool_restriction_by_role() -> None:
    engine = PolicyEngine()
    result = engine.evaluate({"role": "viewer", "tool_name": "calculator"})
    assert result.allowed is False
    assert any("tool" in v.lower() for v in result.violations)


def test_tool_allowed_for_role() -> None:
    engine = PolicyEngine()
    result = engine.evaluate({"role": "viewer", "tool_name": "search"})
    assert result.allowed is True


def test_multiple_violations() -> None:
    engine = PolicyEngine()
    result = engine.evaluate({
        "role": "viewer",
        "risk_tier": 0,
        "pii_detected": True,
        "privacy_tier": 0,
        "tool_name": "calculator",
    })
    assert result.allowed is False
    assert len(result.violations) >= 2


def test_policy_version_included() -> None:
    engine = PolicyEngine()
    result = engine.evaluate({"role": "admin"})
    assert result.policy_version == "1.0.0"
