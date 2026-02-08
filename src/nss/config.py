"""NSS configuration via environment variables with NSS_ prefix.

Uses pydantic-settings to load all configuration from environment variables.
Every setting can be overridden by setting NSS_<SETTING_NAME> in the environment.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings


class NSSConfig(BaseSettings):
    """Central configuration for all NSS components.

    All values can be overridden via environment variables prefixed with ``NSS_``.
    For example, ``NSS_GATEWAY_PORT=8080`` overrides :pyattr:`gateway_port`.
    """

    model_config = {"env_prefix": "NSS_"}

    # -- Network bindings ------------------------------------------------
    gateway_host: str = "127.0.0.1"
    gateway_port: int = 11337
    guardian_port: int = 11338
    governance_port: int = 11339
    metrics_port: int = 11340

    # -- Ollama / LLM ----------------------------------------------------
    ollama_base_url: str = "http://localhost:11434"
    ollama_small_model: str = "mistral:7b-instruct-v0.3"
    ollama_large_model: str = "mistral-nemo:12b"

    # -- Qdrant ----------------------------------------------------------
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # -- Redis -----------------------------------------------------------
    redis_url: str = "redis://localhost:6379/0"

    # -- Security --------------------------------------------------------
    hmac_secret: str = "change-me-in-production"
    jwt_secret: str = "change-me-in-production"
    jwt_expiry_minutes: int = 15

    # -- Privacy ---------------------------------------------------------
    privacy_epsilon_budget: float = 1.0

    # -- Guardian thresholds ---------------------------------------------
    apex_confidence_threshold: float = 0.85
    sentinel_consensus_threshold: int = 2
    vigil_rate_limit: int = 100

    # -- Logging ---------------------------------------------------------
    log_level: str = "INFO"


# Module-level singleton (import and use directly).
config = NSSConfig()
