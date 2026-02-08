"""Tests for privacy budget tracker."""

from nss.governance.privacy_budget import PrivacyBudgetTracker


def test_consume_within_budget() -> None:
    tracker = PrivacyBudgetTracker(total_budget=1.0)
    assert tracker.consume(0.1, "user-1") is True


def test_budget_exhausted() -> None:
    tracker = PrivacyBudgetTracker(total_budget=0.5)
    tracker.consume(0.3, "user-1")
    tracker.consume(0.2, "user-1")
    assert tracker.consume(0.1, "user-1") is False


def test_remaining() -> None:
    tracker = PrivacyBudgetTracker(total_budget=1.0)
    tracker.consume(0.3, "user-1")
    assert abs(tracker.remaining("user-1") - 0.7) < 1e-9


def test_reset() -> None:
    tracker = PrivacyBudgetTracker(total_budget=1.0)
    tracker.consume(0.5, "user-1")
    tracker.reset("user-1")
    assert tracker.remaining("user-1") == 1.0


def test_independent_users() -> None:
    tracker = PrivacyBudgetTracker(total_budget=1.0)
    tracker.consume(0.8, "user-1")
    assert tracker.remaining("user-2") == 1.0
