"""VIGIL tool-call safety validator.

Checks tool invocations against an allow-list and enforces rate limits
to maintain confidentiality, integrity, and availability.
"""

from __future__ import annotations

import time
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

ALLOWED_TOOLS: set[str] = {
    "search",
    "calculator",
    "calendar",
    "weather",
    "translator",
    "summarizer",
    "document_reader",
}

# Per-user, per-tool rate-limit state: {user_id: {tool_name: [(timestamp, ...)]}}
_rate_limits: dict[str, dict[str, list[float]]] = {}

_DEFAULT_WINDOW_SECONDS: int = 60


def _prune_window(
    timestamps: list[float],
    window: int = _DEFAULT_WINDOW_SECONDS,
) -> list[float]:
    """Remove timestamps older than *window* seconds."""
    cutoff = time.time() - window
    return [t for t in timestamps if t > cutoff]


def check_tool_call(
    tool_name: str,
    args: dict[str, Any],
    user_id: str,
    rate_limit: int = 100,
) -> dict[str, Any]:
    """Validate a tool invocation for safety.

    Performs three checks:
        1. **Confidentiality** -- is the tool on the allow-list?
        2. **Integrity** -- are the arguments well-formed (non-empty, no
           suspicious patterns)?
        3. **Availability** -- has the user exceeded the per-tool rate limit?

    Args:
        tool_name: Name of the tool being invoked.
        args: Argument dictionary passed to the tool.
        user_id: Identifier of the calling user.
        rate_limit: Maximum invocations per window (default 100).

    Returns:
        A dict with ``verdict`` (``"ALLOW"`` or ``"DENY"``), ``reasons``
        (list of human-readable explanations), and per-check results.
    """
    reasons: list[str] = []
    checks: dict[str, bool] = {}

    # 1. Confidentiality: allow-list
    confidentiality_ok = tool_name in ALLOWED_TOOLS
    checks["confidentiality"] = confidentiality_ok
    if not confidentiality_ok:
        reasons.append(f"Tool '{tool_name}' is not in the allow-list.")

    # 2. Integrity: argument validation
    integrity_ok = True
    if not isinstance(args, dict):
        integrity_ok = False
        reasons.append("Arguments must be a dict.")
    else:
        for key, value in args.items():
            str_val = str(value)
            # Reject suspiciously long values or known shell meta-characters
            if len(str_val) > 10_000:
                integrity_ok = False
                reasons.append(f"Argument '{key}' exceeds maximum length.")
            if any(c in str_val for c in [";", "|", "`", "$("]):
                integrity_ok = False
                reasons.append(f"Argument '{key}' contains suspicious characters.")
    checks["integrity"] = integrity_ok

    # 3. Availability: rate limiting
    user_limits = _rate_limits.setdefault(user_id, {})
    tool_ts = user_limits.setdefault(tool_name, [])
    tool_ts[:] = _prune_window(tool_ts)

    availability_ok = len(tool_ts) < rate_limit
    checks["availability"] = availability_ok
    if not availability_ok:
        reasons.append(
            f"Rate limit exceeded for tool '{tool_name}' "
            f"({len(tool_ts)}/{rate_limit} in last {_DEFAULT_WINDOW_SECONDS}s)."
        )

    # Record this call
    if availability_ok:
        tool_ts.append(time.time())

    verdict = "ALLOW" if all(checks.values()) else "DENY"

    if verdict == "DENY":
        logger.warning(
            "vigil_denied",
            tool=tool_name,
            user_id=user_id,
            reasons=reasons,
        )

    return {
        "verdict": verdict,
        "reasons": reasons,
        "checks": checks,
    }
