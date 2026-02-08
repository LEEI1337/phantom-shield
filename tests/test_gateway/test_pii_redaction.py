"""Tests for PII redaction functionality."""

from nss.gateway.pii_redaction import redact_pii


def test_redact_email() -> None:
    text = "Contact me at john@example.com please"
    result, entities = redact_pii(text)
    assert "[REDACTED_EMAIL]" in result
    assert "john@example.com" not in result
    assert len(entities) >= 1


def test_redact_phone() -> None:
    text = "Call me at +43 123 456789"
    result, entities = redact_pii(text)
    assert "[REDACTED_PHONE]" in result


def test_redact_iban() -> None:
    text = "My IBAN is AT123456789012345678"
    result, entities = redact_pii(text)
    assert "[REDACTED_IBAN]" in result


def test_redact_credit_card() -> None:
    text = "Card number 4111111111111111"
    result, entities = redact_pii(text)
    assert "[REDACTED_CREDIT_CARD]" in result


def test_redact_ipv4() -> None:
    text = "Server at 192.168.1.100"
    result, entities = redact_pii(text)
    assert "[REDACTED_IP]" in result


def test_no_pii() -> None:
    text = "This is a normal message with no sensitive data."
    result, entities = redact_pii(text)
    assert result == text
    assert len(entities) == 0


def test_multiple_pii() -> None:
    text = "Email john@test.com and call +49 30 12345678"
    result, entities = redact_pii(text)
    assert "[REDACTED_EMAIL]" in result
    assert "[REDACTED_PHONE]" in result
    assert len(entities) >= 2
