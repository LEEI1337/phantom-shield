"""Differential-privacy budget tracker with optional Redis persistence.

Maintains per-user epsilon budgets to enforce cumulative privacy
guarantees across multiple queries.  When a ``redis_url`` is supplied
the tracker persists every budget change to Redis hashes, allowing
budgets to survive process restarts and be shared across replicas.
"""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)

_REDIS_HASH = "nss:privacy:budgets"


class PrivacyBudgetTracker:
    """Per-user differential-privacy epsilon budget manager.

    Parameters:
        total_budget: Maximum epsilon each user may consume before being
            refused further queries (default ``1.0``).
        redis_url: Optional Redis connection URL for durable persistence.
            Falls back to in-memory tracking when unavailable.
    """

    def __init__(self, total_budget: float = 1.0, redis_url: str = "") -> None:
        self.total_budget = total_budget
        self._budgets: dict[str, float] = {}
        self._redis: Any | None = None
        if redis_url:
            try:
                import redis as _redis

                self._redis = _redis.Redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
                logger.info("privacy_budget_redis_connected", url=redis_url)
            except Exception:
                self._redis = None
                logger.warning("privacy_budget_redis_unavailable", url=redis_url)

    # ------------------------------------------------------------------

    def _ensure_user(self, user_id: str) -> None:
        """Initialise the budget for *user_id* if not already present."""
        if user_id not in self._budgets:
            # Try to restore from Redis first
            if self._redis is not None:
                try:
                    stored = self._redis.hget(_REDIS_HASH, user_id)
                    if stored is not None:
                        self._budgets[user_id] = float(stored)
                        return
                except Exception:
                    pass  # fall through to default
            self._budgets[user_id] = self.total_budget

    def _persist(self, user_id: str) -> None:
        """Best-effort write of the current budget to Redis."""
        if self._redis is not None:
            try:
                self._redis.hset(_REDIS_HASH, user_id, str(self._budgets[user_id]))
            except Exception:
                logger.warning("privacy_budget_redis_write_failed", user_id=user_id)

    # ------------------------------------------------------------------

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
        self._persist(user_id)
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
        self._persist(user_id)
        logger.info("privacy_budget_reset", user_id=user_id)

    @property
    def redis_available(self) -> bool:
        """Whether Redis persistence is active."""
        return self._redis is not None
