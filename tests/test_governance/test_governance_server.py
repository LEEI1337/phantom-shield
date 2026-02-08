"""Tests for Governance Plane API server."""

import pytest
from httpx import AsyncClient, ASGITransport

from nss.governance.server import app


async def test_health() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["service"] == "governance-plane"


async def test_policy_evaluate() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/v1/policy/evaluate", json={"role": "admin"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["allowed"] is True


async def test_privacy_budget() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/v1/privacy/budget/user-1")
        assert resp.status_code == 200
        data = resp.json()
        assert "remaining_epsilon" in data


async def test_dpia_generate() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/v1/dpia/generate", json={
            "processing_activity": "LLM query",
            "data_categories": ["email"],
            "risk_tier": 2,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "report_id" in data
        assert "sections" in data


async def test_audit_trail() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First create an audit event via policy evaluation
        await client.post("/v1/policy/evaluate", json={"role": "viewer"})
        # Then retrieve all audit entries
        resp = await client.get("/v1/audit")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1
