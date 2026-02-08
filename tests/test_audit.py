"""Tests for audit logging with hash chain integrity."""

from nss.audit import AuditLogger


def test_log_event_returns_audit_id() -> None:
    logger = AuditLogger()
    audit_id = logger.log_event("test_event", "user-1", "gateway", "pii_redaction")
    assert isinstance(audit_id, str)
    assert len(audit_id) == 36  # UUID format


def test_chain_integrity_valid() -> None:
    logger = AuditLogger()
    logger.log_event("event_1", "user-1", "gateway", "pii_redaction")
    logger.log_event("event_2", "user-1", "guardian", "mars")
    logger.log_event("event_3", "user-2", "governance", "policy_engine")
    assert logger.verify_integrity() is True


def test_chain_integrity_tampered() -> None:
    logger = AuditLogger()
    logger.log_event("event_1", "user-1", "gateway", "pii_redaction")
    logger.log_event("event_2", "user-1", "guardian", "mars")
    # Tamper with an entry
    logger._entries[0]["event"] = "tampered_event"
    assert logger.verify_integrity() is False


def test_get_trail_all() -> None:
    logger = AuditLogger()
    logger.log_event("event_1", "user-1", "gateway", "pii_redaction")
    logger.log_event("event_2", "user-2", "guardian", "mars")
    trail = logger.get_trail()
    assert len(trail) == 2


def test_get_trail_by_id() -> None:
    logger = AuditLogger()
    aid = logger.log_event("event_1", "user-1", "gateway", "pii_redaction")
    logger.log_event("event_2", "user-2", "guardian", "mars")
    trail = logger.get_trail(audit_id=aid)
    assert len(trail) == 1
    assert trail[0]["audit_id"] == aid


def test_entry_has_required_fields() -> None:
    logger = AuditLogger()
    logger.log_event("test", "user-1", "gateway", "test", details={"key": "value"})
    entry = logger._entries[0]
    assert "audit_id" in entry
    assert "timestamp_us" in entry
    assert "integrity_hash" in entry
    assert "previous_hash" in entry
    assert entry["details"] == {"key": "value"}
