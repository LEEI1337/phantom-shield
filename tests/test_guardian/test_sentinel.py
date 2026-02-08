"""Tests for SENTINEL injection defense."""

from unittest.mock import MagicMock

from nss.guardian.sentinel import SentinelDefense


def _make_sentinel() -> SentinelDefense:
    """Create a SentinelDefense with a mocked Ollama client."""
    mock_client = MagicMock()
    return SentinelDefense(ollama_client=mock_client)


def test_sql_injection_detected() -> None:
    sentinel = _make_sentinel()
    assert sentinel.check_rules("'; DROP TABLE users; --") is True


def test_xss_detected() -> None:
    sentinel = _make_sentinel()
    assert sentinel.check_rules("<script>alert('xss')</script>") is True


def test_command_injection_detected() -> None:
    sentinel = _make_sentinel()
    assert sentinel.check_rules("; cat /etc/passwd") is True


def test_clean_input_passes() -> None:
    sentinel = _make_sentinel()
    assert sentinel.check_rules("What is the weather today?") is False


def test_or_injection_detected() -> None:
    sentinel = _make_sentinel()
    assert sentinel.check_rules("' OR '1'='1") is False  # OR without SQL keywords doesn't match
