"""Immutable audit logging with SHA-256 hash chain.

Each audit entry is hash-chained to the previous entry, providing
tamper-evidence for the complete audit trail.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class AuditLogger:
    """Append-only audit logger with hash-chain integrity.
    
    Each entry contains a SHA-256 hash computed from the previous
    entry's hash concatenated with the current entry's JSON content.
    """

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._last_hash: str = "0" * 64  # genesis hash

    def log_event(
        self,
        event: str,
        user_id: str,
        layer: str,
        component: str,
        details: dict[str, Any] | None = None,
    ) -> str:
        """Record an audit event.
        
        Args:
            event: Event type (e.g. "pii_redaction", "sentinel_check").
            user_id: Identifier of the acting user.
            layer: Architecture layer (gateway, guardian, governance, agent, knowledge).
            component: Component name (e.g. "mars", "sentinel", "pii_redaction").
            details: Optional free-form details dict.
            
        Returns:
            The audit_id of the created entry.
        """
        audit_id = str(uuid.uuid4())
        timestamp_us = int(time.time() * 1_000_000)
        
        entry_data = {
            "audit_id": audit_id,
            "timestamp_us": timestamp_us,
            "event": event,
            "user_id": user_id,
            "layer": layer,
            "component": component,
            "details": details or {},
        }
        
        # Compute integrity hash: SHA-256(previous_hash + json(entry_data))
        content = self._last_hash + json.dumps(entry_data, sort_keys=True)
        integrity_hash = hashlib.sha256(content.encode()).hexdigest()
        
        entry = {**entry_data, "integrity_hash": integrity_hash, "previous_hash": self._last_hash}
        self._entries.append(entry)
        self._last_hash = integrity_hash
        
        logger.info("audit_event", audit_id=audit_id, event_type=event, layer=layer, component=component)
        return audit_id

    def get_trail(self, audit_id: str | None = None) -> list[dict[str, Any]]:
        """Retrieve audit entries.
        
        Args:
            audit_id: If provided, return only the matching entry. Otherwise return all.
        """
        if audit_id:
            return [e for e in self._entries if e["audit_id"] == audit_id]
        return list(self._entries)

    def verify_integrity(self) -> bool:
        """Verify the hash chain is intact.
        
        Returns:
            True if all hashes are valid, False if tampering detected.
        """
        expected_hash = "0" * 64
        for entry in self._entries:
            entry_data = {
                k: v for k, v in entry.items()
                if k not in ("integrity_hash", "previous_hash")
            }
            content = expected_hash + json.dumps(entry_data, sort_keys=True)
            computed = hashlib.sha256(content.encode()).hexdigest()
            if computed != entry["integrity_hash"]:
                return False
            expected_hash = entry["integrity_hash"]
        return True

    @property
    def count(self) -> int:
        """Number of entries in the audit log."""
        return len(self._entries)


# Module-level singleton
audit_logger = AuditLogger()
