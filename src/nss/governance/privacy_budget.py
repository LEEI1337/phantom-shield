"""Differential-privacy budget tracker.

Maintains per-user epsilon budgets to enforce cumulative privacy
guarantees across multiple queries.
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


class PrivacyBudgetTracker:
    """Per-user differential-privacy epsilon budget manager.

    Parameters:
        total_budget: Maximum epsilon each user may consume before being
            refused further queries (default ``1.0``).
    """

    def __init__(self, total_budget: float = 1.0) -> None:
        self.total_budget = total_budget
        self._budgets: dict[str, float] = {}

    def _ensure_user(self, user_id: str) -> None:
        """Initialise the budget for *user_id* if not already present."""
        if user_id not in self._budgets:
            self._budgets[user_id] = self.total_budget

    def consume(self, epsilon: float, user_id: str) -> bool:
        """Attempt to consume *epsilon* from *user_id*'s budget.

        Args:
            epsilon: Amount of privacy budget to spend.
            user_id: The user whose budget is affected.

        Returns:
            ``True`` if the budget was sufficient and has been decremented,
            ``False`` if the request would exceed the remaining budget.
        """
        self._ensure_user(user_id)

        if epsilon < 0:
            logger.warning("negative_epsilon_requested", user_id=user_id, epsilon=epsilon)
            return False

        if self._budgets[user_id] < epsilon:
            logger.info(
                "privacy_budget_exhausted",
                user_id=user_id,
                remaining=self._budgets[user_id],
                requested=epsilon,
            )
            return False

        self._budgets[user_id] -= epsilon
        logger.debug(
            "privacy_budget_consumed",
            user_id=user_id,
            consumed=epsilon,
            remaining=self._budgets[user_id],
        )
        return True

    def remaining(self, user_id: str) -> float:
        """Return the remaining epsilon budget for *user_id*.

        If the user has never been seen, returns :pyattr:`total_budget`.
        """
        self._ensure_user(user_id)
        return self._budgets[user_id]

    def reset(self, user_id: str) -> None:
        """Reset *user_id*'s budget to the full :pyattr:`total_budget`."""
        self._budgets[user_id] = self.total_budget
        logger.info("privacy_budget_reset", user_id=user_id)
