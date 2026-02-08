"""MARS (Model Audit & Risk Scoring) -- LLM-assisted risk evaluation.

Uses Ollama to analyse free-text input and produce a numeric risk score
which is then classified into one of four tiers.
"""

from __future__ import annotations

import re

import structlog

from nss.llm.ollama_client import OllamaClient
from nss.models import RiskScore

logger = structlog.get_logger(__name__)

_RISK_PROMPT_TEMPLATE = (
    "Analyse the following text for potential security risks, "
    "harmful intent, or policy violations.  Respond with ONLY a JSON object:\n"
    '{{"score": <float 0-1>, "category": "<risk category>", '
    '"details": "<brief explanation>"}}\n\n'
    "Text ({language}):\n"
    '\"\"\"\n{text}\n\"\"\"'
)

# -- Tier classification -----------------------------------------------------

_TIER_BOUNDARIES: list[tuple[float, float, int, str]] = [
    (0.95, 1.00, 0, "CRITICAL"),
    (0.90, 0.95, 1, "HIGH"),
    (0.85, 0.90, 2, "MEDIUM"),
    (0.80, 0.85, 3, "LOW"),
]


def classify_tier(score: float) -> int:
    """Map a raw risk score to a tier (0-3).

    Tier boundaries:
        - 0.95 -- 1.00  ->  Tier 0 (CRITICAL)
        - 0.90 -- 0.95  ->  Tier 1 (HIGH)
        - 0.85 -- 0.90  ->  Tier 2 (MEDIUM)
        - 0.80 -- 0.85  ->  Tier 3 (LOW)
        - below 0.80     ->  Tier 3 (LOW, safest bucket)

    Args:
        score: Risk score in [0, 1].

    Returns:
        Integer tier from 0 (most dangerous) to 3 (least dangerous).
    """
    for lower, upper, tier, _label in _TIER_BOUNDARIES:
        if lower <= score <= upper:
            return tier
    return 3  # Below 0.80 -> safest tier


class MARSScorer:
    """MARS risk-scoring engine backed by an Ollama model.

    Parameters:
        ollama_client: An initialised :class:`OllamaClient`.
    """

    def __init__(self, ollama_client: OllamaClient) -> None:
        self._llm = ollama_client

    async def score_risk(self, text: str, language: str = "de") -> RiskScore:
        """Evaluate the risk level of *text*.

        Args:
            text: User-supplied content to analyse.
            language: ISO-639-1 language hint (default ``de``).

        Returns:
            A fully populated :class:`RiskScore`.
        """
        prompt = _RISK_PROMPT_TEMPLATE.format(text=text, language=language)

        try:
            raw = await self._llm.generate(
                prompt=prompt,
                system_prompt="You are a security analyst.  Respond ONLY with valid JSON.",
            )

            # Try to extract JSON from the response
            score = 0.0
            category = "UNKNOWN"
            details = raw

            score_match = re.search(r'"score"\s*:\s*([\d.]+)', raw)
            if score_match:
                score = min(max(float(score_match.group(1)), 0.0), 1.0)

            cat_match = re.search(r'"category"\s*:\s*"([^"]+)"', raw)
            if cat_match:
                category = cat_match.group(1)

            det_match = re.search(r'"details"\s*:\s*"([^"]+)"', raw)
            if det_match:
                details = det_match.group(1)

        except Exception:
            logger.exception("mars_scoring_failed")
            score = 0.5
            category = "ERROR"
            details = "MARS scoring failed; defaulting to medium risk."

        tier = classify_tier(score)
        return RiskScore(score=score, tier=tier, category=category, details=details)
