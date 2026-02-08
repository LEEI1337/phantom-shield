"""Regex-based PII detection and redaction for GDPR compliance.

Supports common European PII patterns: email addresses, phone numbers
(DE / AT / EU formats), IBANs, credit-card numbers, and IPv4 addresses.
"""

from __future__ import annotations

import re

from nss.models import RedactedEntity

# -- Pattern definitions -----------------------------------------------------

_PII_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "EMAIL",
        re.compile(
            r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
        ),
    ),
    (
        "PHONE",
        re.compile(
            r"(?:\+\d{1,3}[\s\-]?)?(?:\(?\d{2,5}\)?[\s\-]?)?\d[\d\s\-]{5,12}\d",
        ),
    ),
    (
        "IBAN",
        re.compile(
            r"\b[A-Z]{2}\d{2}[\s]?[\dA-Z]{4}[\s]?(?:[\dA-Z]{4}[\s]?){2,7}[\dA-Z]{1,4}\b",
        ),
    ),
    (
        "CREDIT_CARD",
        re.compile(
            r"\b(?:\d{4}[\s\-]?){3}\d{4}\b",
        ),
    ),
    (
        "IPV4",
        re.compile(
            r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b",
        ),
    ),
]


def redact_pii(text: str) -> tuple[str, list[RedactedEntity]]:
    """Scan *text* for PII and replace matches with ``[REDACTED_<TYPE>]``.

    Args:
        text: Arbitrary input string.

    Returns:
        A tuple of ``(redacted_text, entities)`` where *entities* lists every
        PII match found (with offsets relative to the **original** text).
    """
    entities: list[RedactedEntity] = []

    # We process from the end so that earlier offsets remain valid.
    all_matches: list[tuple[str, re.Match[str]]] = []
    for label, pattern in _PII_PATTERNS:
        for m in pattern.finditer(text):
            all_matches.append((label, m))

    # Sort by start position descending so replacements don't shift offsets.
    all_matches.sort(key=lambda pair: pair[1].start(), reverse=True)

    redacted = text
    for label, m in all_matches:
        entities.append(
            RedactedEntity(
                entity_type=label,
                original_length=m.end() - m.start(),
                start=m.start(),
                end=m.end(),
            )
        )
        redacted = redacted[: m.start()] + f"[REDACTED_{label}]" + redacted[m.end() :]

    # Return entities in document order (ascending start).
    entities.reverse()
    return redacted, entities
