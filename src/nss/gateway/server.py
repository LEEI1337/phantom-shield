"""Cognitive Gateway -- FastAPI application serving the NSS processing pipeline.

Binds to 127.0.0.1 only (no external exposure by default).
Pipeline: PII redaction -> STEER transform -> PNC compression -> SENTINEL check
          -> MARS scoring -> APEX routing -> SHIELD enhancement -> LLM generation.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from nss import __version__
from nss.audit import AuditLogger
from nss.cache import CacheLayer
from nss.config import config
from nss.gateway.hmac_signing import verify_request
from nss.gateway.pii_redaction import redact_pii
from nss.gateway.pnc_compression import compress
from nss.gateway.steer import steer_transform
from nss.guardian.apex import APEXRouter
from nss.guardian.mars import MARSScorer
from nss.guardian.sentinel import SentinelDefense
from nss.guardian.shield import enhance_prompt
from nss.llm.ollama_client import OllamaClient
from nss.metrics import (
    metrics_snapshot,
    nss_guardian_latency,
    nss_pii_entities_redacted,
    nss_request_latency,
    nss_requests_blocked,
    nss_requests_total,
)
from nss.middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    TracingMiddleware,
)
from nss.models import NSSRequest, NSSResponse

logger = structlog.get_logger(__name__)

# -- Shared state (populated during lifespan) --------------------------------
_ollama_client: OllamaClient | None = None
_mars_scorer: MARSScorer | None = None
_apex_router: APEXRouter | None = None
_sentinel: SentinelDefense | None = None
_audit_logger: AuditLogger | None = None
_cache: CacheLayer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown hook for the gateway."""
    global _ollama_client, _mars_scorer, _apex_router, _sentinel, _audit_logger, _cache

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
    _audit_logger = AuditLogger()

    # Cache layer (graceful -- works without Redis)
    _cache = CacheLayer(redis_url=config.redis_url)
    try:
        await _cache.connect()
        logger.info("cache_connected", redis_url=config.redis_url)
    except Exception:
        logger.warning("cache_unavailable", redis_url=config.redis_url)

    logger.info("gateway_ready")
    yield

    # Shutdown
    if _cache is not None:
        await _cache.close()
    if _ollama_client is not None:
        await _ollama_client.close()
    logger.info("gateway_stopped")


app = FastAPI(
    title="NSS Cognitive Gateway",
    version=__version__,
    lifespan=lifespan,
)

# -- Middleware (LIFO order: first added = innermost) -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, max_requests=config.rate_limit_rpm, window_seconds=60)
app.add_middleware(TracingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


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
    """Return operational metrics from the metrics registry."""
    return metrics_snapshot()


@app.post("/v1/process", response_model=NSSResponse)
async def process(request: NSSRequest) -> NSSResponse:
    """Run the full NSS processing pipeline on an inbound request.

    Steps:
        1. PII redaction
        2. STEER transformation (language detection, privacy-tier context)
        3. PNC compression (deduplication, filler removal, token budget)
        4. SENTINEL injection check
        5. MARS risk scoring
        6. APEX model routing
        7. SHIELD prompt enhancement
        8. LLM generation (with cache)
    """
    assert _ollama_client is not None
    assert _mars_scorer is not None
    assert _apex_router is not None
    assert _sentinel is not None
    assert _audit_logger is not None

    start = time.perf_counter()
    audit_id = str(uuid.uuid4())
    nss_requests_total.inc()

    # 1. PII Redaction
    redacted_message, entities = redact_pii(request.message)
    if entities:
        nss_pii_entities_redacted.inc(len(entities))
        logger.info("pii_redacted", audit_id=audit_id, count=len(entities))
    _audit_logger.log_event(
        "pii_redaction",
        user_id=request.user_id,
        layer="gateway",
        component="pii_redaction",
        details={"entities_count": len(entities), "audit_id": audit_id},
    )

    # 2. STEER Transformation
    transformed_message, steer_meta = steer_transform(
        redacted_message, privacy_tier=request.privacy_tier,
    )

    # 3. PNC Compression
    compressed_message, compression_ratio, pnc_meta = compress(transformed_message)

    # 4. SENTINEL injection check
    guardian_start = time.perf_counter()
    sentinel_result = await _sentinel.check_injection(compressed_message)
    _audit_logger.log_event(
        "sentinel_check",
        user_id=request.user_id,
        layer="guardian",
        component="sentinel",
        details={
            "is_safe": sentinel_result.is_safe,
            "confidence": sentinel_result.confidence,
            "audit_id": audit_id,
        },
    )
    if not sentinel_result.is_safe:
        nss_requests_blocked.inc()
        raise HTTPException(
            status_code=422,
            detail=f"Request blocked by SENTINEL: {sentinel_result.consensus}",
        )

    # 5. MARS risk scoring
    risk = await _mars_scorer.score_risk(compressed_message)
    _audit_logger.log_event(
        "mars_scoring",
        user_id=request.user_id,
        layer="guardian",
        component="mars",
        details={"score": risk.score, "tier": risk.tier, "audit_id": audit_id},
    )

    # 6. APEX model routing
    decision = _apex_router.select_model(
        query=compressed_message,
        confidence=sentinel_result.confidence,
        budget_remaining=1.0,
    )

    guardian_elapsed_ms = (time.perf_counter() - guardian_start) * 1000
    nss_guardian_latency.observe(guardian_elapsed_ms)

    # 7. SHIELD prompt enhancement
    safe_prompt = enhance_prompt(compressed_message)

    # 8. LLM generation (with cache)
    cache_key = hashlib.sha256(
        f"{safe_prompt}:{decision.model_selected}".encode(),
    ).hexdigest()

    response_text = None
    if _cache is not None:
        try:
            response_text = await _cache.get("gateway", cache_key)
        except Exception:
            pass  # graceful degradation

    if response_text is None:
        response_text = await _ollama_client.generate(
            prompt=safe_prompt,
            model=decision.model_selected,
        )
        if _cache is not None:
            try:
                await _cache.set("gateway", cache_key, response_text)
            except Exception:
                pass  # graceful degradation

    _audit_logger.log_event(
        "llm_generation",
        user_id=request.user_id,
        layer="gateway",
        component="ollama",
        details={
            "model": decision.model_selected,
            "audit_id": audit_id,
            "cache_hit": response_text is not None,
        },
    )

    elapsed_ms = (time.perf_counter() - start) * 1000
    nss_request_latency.observe(elapsed_ms)

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
