"""Tests for VIGIL tool call safety."""

from nss.guardian.vigil import VIGILChecker


def test_allowed_tool_passes() -> None:
    vigil = VIGILChecker()
    result = vigil.check_tool_call("database_query", {"query": "SELECT 1"}, "user-1")
    assert result["verdict"] == "ALLOW"


def test_unknown_tool_blocked() -> None:
    vigil = VIGILChecker()
    result = vigil.check_tool_call("dangerous_tool", {}, "user-1")
    assert result["verdict"] == "DENY"


def test_pii_in_args_blocked() -> None:
    vigil = VIGILChecker()
    result = vigil.check_tool_call(
        "database_query",
        {"query": "SELECT * WHERE email='john@example.com'"},
        "user-1",
    )
    assert result["confidentiality"]["contains_pii"] is True
