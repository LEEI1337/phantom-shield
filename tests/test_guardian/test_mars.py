"""Tests for the MARS risk-scoring module."""

import pytest

from nss.guardian.mars import MARSScorer, classify_tier
from nss.models import RiskScore


class TestClassifyTier:
    """Unit tests for the classify_tier function."""

    def test_classify_tier_critical(self) -> None:
        """Score 0.97 should map to tier 0 (CRITICAL)."""
        assert classify_tier(0.97) == 0

    def test_classify_tier_high(self) -> None:
        """Score 0.92 should map to tier 1 (HIGH)."""
        assert classify_tier(0.92) == 1

    def test_classify_tier_medium(self) -> None:
        """Score 0.87 should map to tier 2 (MEDIUM)."""
        assert classify_tier(0.87) == 2

    def test_classify_tier_low(self) -> None:
        """Score 0.82 should map to tier 3 (LOW)."""
        assert classify_tier(0.82) == 3

    def test_classify_tier_below_low(self) -> None:
        """Score 0.5 (below 0.80) should map to tier 3 (safest bucket)."""
        assert classify_tier(0.5) == 3


class TestMARSScorer:
    """Tests for the MARSScorer async risk evaluation."""

    async def test_score_risk_with_mock(self, mock_ollama_client) -> None:
        """score_risk should parse the mocked JSON and return a RiskScore."""
        scorer = MARSScorer(ollama_client=mock_ollama_client)
        result = await scorer.score_risk("Test input text", language="en")

        assert isinstance(result, RiskScore)
        assert result.score == pytest.approx(0.15)
        assert result.category == "LOW_RISK"
        assert result.details == "No issues found."
        assert result.tier == 3  # 0.15 is below 0.80 -> tier 3
        mock_ollama_client.generate.assert_awaited_once()
