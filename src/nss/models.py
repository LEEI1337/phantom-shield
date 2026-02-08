"""Pydantic v2 data models used across all NSS components."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class NSSRequest(BaseModel):
    """Inbound request to the Cognitive Gateway.

    Attributes:
        user_id: Authenticated user identifier.
        message: The user's natural-language query.
        privacy_tier: GDPR privacy tier (0-3, where 0 = public, 3 = maximum protection).
        metadata: Arbitrary key-value pairs forwarded through the pipeline.
    """

    user_id: str
    message: str
    privacy_tier: int = Field(default=0, ge=0, le=3)
    metadata: dict[str, Any] = Field(default_factory=dict)


class NSSResponse(BaseModel):
    """Outbound response from the Cognitive Gateway.

    Attributes:
        response: The generated text answer.
        risk_score: MARS risk score in [0, 1].
        model_used: Identifier of the model that produced the response.
        latency_ms: End-to-end latency in milliseconds.
        privacy_tier: Privacy tier applied during processing.
        audit_id: Unique identifier for the audit trail entry.
    """

    response: str
    risk_score: float
    model_used: str
    latency_ms: float
    privacy_tier: int
    audit_id: str


class RiskScore(BaseModel):
    """Result of a MARS risk evaluation.

    Attributes:
        score: Numeric risk score in [0, 1].
        tier: Classified risk tier (0-3).
        category: Human-readable risk category label.
        details: Explanation of how the score was derived.
    """

    score: float = Field(ge=0.0, le=1.0)
    tier: int = Field(ge=0, le=3)
    category: str
    details: str


class SentinelResult(BaseModel):
    """Outcome of SENTINEL injection-defence analysis.

    Attributes:
        is_safe: ``True`` when the input passes all checks.
        confidence: Aggregated confidence score in [0, 1].
        method_results: Per-method pass/fail mapping.
        consensus: Human-readable summary of the consensus decision.
    """

    is_safe: bool
    confidence: float = Field(ge=0.0, le=1.0)
    method_results: dict[str, bool]
    consensus: str


class APEXDecision(BaseModel):
    """APEX model-routing decision.

    Attributes:
        model_selected: Identifier of the chosen model.
        confidence: Router confidence in the decision.
        cost_estimate: Estimated cost for the selected model (relative units).
        reason: Human-readable justification for the routing choice.
    """

    model_selected: str
    confidence: float
    cost_estimate: float
    reason: str


class RedactedEntity(BaseModel):
    """Record of a single PII entity that was redacted.

    Attributes:
        entity_type: Category of PII (e.g. ``EMAIL``, ``IBAN``).
        original_length: Character length of the original value.
        start: Start offset in the *original* text.
        end: End offset in the *original* text (exclusive).
    """

    entity_type: str
    original_length: int
    start: int
    end: int
