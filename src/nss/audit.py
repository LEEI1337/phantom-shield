"""Immutable audit logging with SHA-256 hash chain and optional Redis persistence.

Each audit entry is hash-chained to the previous entry, providing
tamper-evidence for the complete audit trail.  When a ``redis_url``
is supplied the logger persists every entry to a Redis list
(``nss:audit:log``) in addition to the in-memory chain, providing
durable storage that survives process restarts.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

_REDIS_KEY = "nss:audit:log"


class AuditLogger:
    """Append-only audit logger with hash-chain integrity.

    Each entry contains a SHA-256 hash computed from the previous
    entry's hash concatenated with the current entry's JSON content.

    Parameters:
        redis_url: Optional Redis connection URL.  When provided the
            logger will persist entries via ``RPUSH`` in addition to
            keeping them in memory.  A connection failure is **not**
            fatal -- the logger gracefully degrades to in-memory only.
    """

    def __init__(self, redis_url: str = "") -> None:
        self._entries: list[dict[str, Any]] = []
        self._last_hash: str = "0" * 64  # genesis hash
        self._redis: Any | None = None
        if redis_url:
            try:
                import redis as _redis

                self._redis = _redis.Redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
                logger.info("audit_redis_connected", url=redis_url)
            except Exception:
                self._redis = None
                logger.warning("audit_redis_unavailable", url=redis_url)

    # ------------------------------------------------------------------

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

        # Persist to Redis (best-effort)
        if self._redis is not None:
            try:
                self._redis.rpush(_REDIS_KEY, json.dumps(entry, sort_keys=True))
            except Exception:
                logger.warning("audit_redis_write_failed", audit_id=audit_id)

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

    @property
    def redis_available(self) -> bool:
        """Whether Redis persistence is active."""
        return self._redis is not None


# Module-level singleton (no Redis by default; servers pass redis_url at init)
audit_logger = AuditLogger()
