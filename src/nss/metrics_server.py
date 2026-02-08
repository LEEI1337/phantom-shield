"""Metrics API server (Port 11340).

Lightweight server exposing NSS operational metrics.
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from nss.auth import JWTMiddleware
from nss.config import config
from nss.metrics import metrics_snapshot, prometheus_export
from nss.middleware import SecurityHeadersMiddleware, TracingMiddleware

app = FastAPI(
    title="NSS Metrics",
    version="3.1.1",
)

app.add_middleware(TracingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(JWTMiddleware, secret=config.jwt_secret)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "metrics"}


@app.get("/metrics")
async def metrics() -> dict:
    return metrics_snapshot()


@app.get("/metrics/prometheus")
async def metrics_prometheus():
    from starlette.responses import PlainTextResponse
    return PlainTextResponse(prometheus_export(), media_type="text/plain; version=0.0.4")


if __name__ == "__main__":
    kwargs = {}
    if config.tls_cert_path and config.tls_key_path:
        kwargs["ssl_certfile"] = config.tls_cert_path
        kwargs["ssl_keyfile"] = config.tls_key_path
    uvicorn.run(
        "nss.metrics_server:app",
        host=config.gateway_host,
        port=config.metrics_port,
        **kwargs,
    )
