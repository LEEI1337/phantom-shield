"""APEX (Adaptive Processing & Execution) intelligent model router.

Selects the optimal model based on query confidence, budget constraints,
and the configured confidence threshold.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nss.models import APEXDecision

if TYPE_CHECKING:
    from nss.config import NSSConfig


class APEXRouter:
    """Route queries to the most cost-effective model.

    Decision logic:
        1. If confidence > threshold  -> use the *small* (cheap) model.
        2. Else if budget remaining   -> use the *large* (expensive) model.
        3. Else                       -> fall back to the small model.

    Parameters:
        config: An :class:`NSSConfig` instance providing model names and
            the confidence threshold.
    """

    def __init__(self, config: NSSConfig) -> None:
        self._small = config.ollama_small_model
        self._large = config.ollama_large_model
        self._threshold = config.apex_confidence_threshold

    def select_model(
        self,
        query: str,
        confidence: float,
        budget_remaining: float,
    ) -> APEXDecision:
        """Choose a model for the given *query*.

        Args:
            query: The (possibly redacted) user query -- used for logging
                only; routing is driven by *confidence* and *budget_remaining*.
            confidence: SENTINEL confidence score in [0, 1].
            budget_remaining: Remaining cost budget (arbitrary units).

        Returns:
            An :class:`APEXDecision` documenting the choice.
        """
        if confidence >= self._threshold:
            return APEXDecision(
                model_selected=self._small,
                confidence=confidence,
                cost_estimate=0.1,
                reason=(
                    f"Confidence {confidence:.2f} >= threshold "
                    f"{self._threshold:.2f}; using cost-efficient small model."
                ),
            )

        if budget_remaining > 0:
            return APEXDecision(
                model_selected=self._large,
                confidence=confidence,
                cost_estimate=0.5,
                reason=(
                    f"Confidence {confidence:.2f} < threshold "
                    f"{self._threshold:.2f}; escalating to large model "
                    f"(budget remaining: {budget_remaining:.2f})."
                ),
            )

        return APEXDecision(
            model_selected=self._small,
            confidence=confidence,
            cost_estimate=0.1,
            reason=(
                "Budget exhausted; falling back to small model despite "
                f"low confidence ({confidence:.2f})."
            ),
        )
