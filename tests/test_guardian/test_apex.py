"""Tests for the APEX intelligent model router."""

from nss.guardian.apex import APEXRouter
from nss.models import APEXDecision


class TestAPEXRouter:
    """Unit tests for APEXRouter.select_model."""

    def test_high_confidence_uses_small(self, mock_config) -> None:
        """High confidence (>= threshold) should select the small model."""
        router = APEXRouter(config=mock_config)
        decision = router.select_model(query="test query", confidence=0.9, budget_remaining=10.0)

        assert isinstance(decision, APEXDecision)
        assert decision.model_selected == mock_config.ollama_small_model
        assert decision.cost_estimate == 0.1

    def test_low_confidence_uses_large(self, mock_config) -> None:
        """Low confidence with available budget should select the large model."""
        router = APEXRouter(config=mock_config)
        decision = router.select_model(query="test query", confidence=0.7, budget_remaining=10.0)

        assert isinstance(decision, APEXDecision)
        assert decision.model_selected == mock_config.ollama_large_model
        assert decision.cost_estimate == 0.5

    def test_no_budget_falls_back_to_small(self, mock_config) -> None:
        """Low confidence with zero budget should fall back to the small model."""
        router = APEXRouter(config=mock_config)
        decision = router.select_model(query="test query", confidence=0.7, budget_remaining=0.0)

        assert isinstance(decision, APEXDecision)
        assert decision.model_selected == mock_config.ollama_small_model
        assert decision.cost_estimate == 0.1

    def test_cost_estimates(self, mock_config) -> None:
        """Verify cost_estimate values for both routing paths."""
        router = APEXRouter(config=mock_config)

        small_decision = router.select_model(query="q", confidence=0.9, budget_remaining=10.0)
        assert small_decision.cost_estimate == 0.1

        large_decision = router.select_model(query="q", confidence=0.7, budget_remaining=10.0)
        assert large_decision.cost_estimate == 0.5

        fallback_decision = router.select_model(query="q", confidence=0.7, budget_remaining=0.0)
        assert fallback_decision.cost_estimate == 0.1
