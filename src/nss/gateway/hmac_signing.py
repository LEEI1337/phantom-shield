"""HMAC-SHA256 request signing and verification.

Provides replay-attack protection via timestamp + nonce validation.
"""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid


def generate_nonce() -> str:
    """Return a UUID4-based nonce string."""
    return str(uuid.uuid4())


def sign_request(
    payload: str,
    secret: str,
    timestamp: str,
    nonce: str,
) -> str:
    """Create an HMAC-SHA256 signature over *payload*.

    The signing message is ``timestamp + nonce + payload`` to bind all three
    values together and prevent mix-and-match replay attacks.

    Args:
        payload: The body content to sign.
        secret: Shared HMAC secret.
        timestamp: ISO-8601 or Unix-epoch string attached to the request.
        nonce: Single-use nonce (see :func:`generate_nonce`).

    Returns:
        Hexadecimal HMAC-SHA256 digest.
    """
    message = f"{timestamp}{nonce}{payload}"
    return hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def verify_request(
    payload: str,
    signature: str,
    secret: str,
    timestamp: str,
    nonce: str,
    max_age: int = 300,
) -> bool:
    """Verify an HMAC-SHA256 signature and check timestamp freshness.

    Args:
        payload: The body content that was signed.
        signature: The hex digest to verify.
        secret: Shared HMAC secret.
        timestamp: The timestamp string used during signing (Unix epoch).
        nonce: The nonce string used during signing.
        max_age: Maximum allowed age in seconds (default 300 = 5 min).

    Returns:
        ``True`` if the signature is valid **and** the timestamp is within
        *max_age* seconds of the current time.
    """
    # Timestamp freshness check
    try:
        ts = float(timestamp)
    except (ValueError, TypeError):
        return False

    if abs(time.time() - ts) > max_age:
        return False

    expected = sign_request(payload, secret, timestamp, nonce)
    return hmac.compare_digest(expected, signature)
