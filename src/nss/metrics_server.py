"""Metrics API server (Port 11340).

Lightweight server exposing NSS operational metrics.
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from nss.config import config
from nss.metrics import metrics_snapshot

app = FastAPI(
    title="NSS Metrics",
    version="3.1.1",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "metrics"}


@app.get("/metrics")
async def metrics() -> dict:
    return metrics_snapshot()


if __name__ == "__main__":
    uvicorn.run(
        "nss.metrics_server:app",
        host=config.gateway_host,
        port=config.metrics_port,
    )
