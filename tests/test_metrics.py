"""Tests for lightweight metrics registry."""

from nss.metrics import Counter, Histogram, metrics_snapshot


def test_counter_increment() -> None:
    c = Counter("test_counter")
    assert c.value == 0.0
    c.inc()
    assert c.value == 1.0
    c.inc(5.0)
    assert c.value == 6.0


def test_histogram_observe() -> None:
    h = Histogram("test_histogram")
    h.observe(10.0)
    h.observe(20.0)
    h.observe(30.0)
    assert h.count == 3
    assert h.avg == 20.0
    snap = h.snapshot()
    assert snap["min"] == 10.0
    assert snap["max"] == 30.0


def test_histogram_empty_avg() -> None:
    h = Histogram("test_histogram")
    assert h.avg == 0.0
    assert h.snapshot()["min"] == 0.0


def test_metrics_snapshot_structure() -> None:
    snap = metrics_snapshot()
    assert "timestamp" in snap
    assert "counters" in snap
    assert "histograms" in snap
    assert "nss_requests_total" in snap["counters"]
    assert "nss_request_latency_ms" in snap["histograms"]
