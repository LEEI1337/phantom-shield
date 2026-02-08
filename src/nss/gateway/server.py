"""Cognitive Gateway -- FastAPI application serving the NSS processing pipeline.

Binds to 127.0.0.1 only (no external exposure by default).
Pipeline: PII redaction -> SENTINEL check -> MARS scoring -> APEX routing -> LLM generation.
"""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from nss import __version__
from nss.config import config
from nss.gateway.hmac_signing import verify_request
from nss.gateway.pii_redaction import redact_pii
from nss.guardian.apex import APEXRouter
from nss.guardian.mars import MARSScorer
from nss.guardian.sentinel import SentinelDefense
from nss.guardian.shield import enhance_prompt
from nss.llm.ollama_client import OllamaClient
from nss.models import NSSRequest, NSSResponse

logger = structlog.get_logger(__name__)

# -- Shared state (populated during lifespan) --------------------------------
_ollama_client: OllamaClient | None = None
_mars_scorer: MARSScorer | None = None
_apex_router: APEXRouter | None = None
_sentinel: SentinelDefense | None = None

# -- Metrics counters --------------------------------------------------------
_metrics: dict[str, Any] = {
    "requests_total": 0,
    "requests_blocked": 0,
    "avg_latency_ms": 0.0,
    "total_latency_ms": 0.0,
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown hook for the gateway."""
    global _ollama_client, _mars_scorer, _apex_router, _sentinel

    logger.info("gateway_starting", version=__version__, port=config.gateway_port)

    _ollama_client = OllamaClient(
        base_url=config.ollama_base_url,
        default_model=config.ollama_small_model,
    )
    _mars_scorer = MARSScorer(ollama_client=_ollama_client)
    _apex_router = APEXRouter(config=config)
    _sentinel = SentinelDefense(
        ollama_client=_ollama_client,
        consensus_threshold=config.sentinel_consensus_threshold,
    )

    logger.info("gateway_ready")
    yield

    # Shutdown
    if _ollama_client is not None:
        await _ollama_client.close()
    logger.info("gateway_stopped")


app = FastAPI(
    title="NSS Cognitive Gateway",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# -- Middleware: request logging ---------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Log every inbound request with timing information."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        latency_ms=round(elapsed_ms, 2),
    )
    return response


# -- Endpoints ---------------------------------------------------------------


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness / readiness probe."""
    return {"status": "healthy", "version": __version__}


@app.get("/metrics")
async def metrics() -> dict[str, Any]:
    """Return basic operational metrics."""
    return {**_metrics}


@app.post("/v1/process", response_model=NSSResponse)
async def process(request: NSSRequest) -> NSSResponse:
    """Run the full NSS processing pipeline on an inbound request.

    Steps:
        1. PII redaction
        2. SENTINEL injection check
        3. MARS risk scoring
        4. APEX model routing
        5. SHIELD prompt enhancement
        6. LLM generation
    """
    assert _ollama_client is not None
    assert _mars_scorer is not None
    assert _apex_router is not None
    assert _sentinel is not None

    start = time.perf_counter()
    audit_id = str(uuid.uuid4())
    _metrics["requests_total"] += 1

    # 1. PII Redaction
    redacted_message, entities = redact_pii(request.message)
    if entities:
        logger.info("pii_redacted", audit_id=audit_id, count=len(entities))

    # 2. SENTINEL injection check
    sentinel_result = await _sentinel.check_injection(redacted_message)
    if not sentinel_result.is_safe:
        _metrics["requests_blocked"] += 1
        raise HTTPException(
            status_code=422,
            detail=f"Request blocked by SENTINEL: {sentinel_result.consensus}",
        )

    # 3. MARS risk scoring
    risk = await _mars_scorer.score_risk(redacted_message)

    # 4. APEX model routing
    decision = _apex_router.select_model(
        query=redacted_message,
        confidence=sentinel_result.confidence,
        budget_remaining=1.0,
    )

    # 5. SHIELD prompt enhancement
    safe_prompt = enhance_prompt(redacted_message)

    # 6. LLM generation
    response_text = await _ollama_client.generate(
        prompt=safe_prompt,
        model=decision.model_selected,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000
    _metrics["total_latency_ms"] += elapsed_ms
    _metrics["avg_latency_ms"] = (
        _metrics["total_latency_ms"] / _metrics["requests_total"]
    )

    return NSSResponse(
        response=response_text,
        risk_score=risk.score,
        model_used=decision.model_selected,
        latency_ms=round(elapsed_ms, 2),
        privacy_tier=request.privacy_tier,
        audit_id=audit_id,
    )


# -- Entrypoint --------------------------------------------------------------


def main() -> None:
    """Launch the Cognitive Gateway via uvicorn."""
    uvicorn.run(
        "nss.gateway.server:app",
        host=config.gateway_host,
        port=config.gateway_port,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    main()
