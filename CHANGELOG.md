# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.1.1-rc2] - 2026-02-09

### Added

- **JWT Authentication**: JWTMiddleware (HS256) enforced on all 4 servers; skip list for `/health`, `/metrics`, `/metrics/prometheus`
- **HMAC Verification**: FastAPI dependency-based HMAC-SHA256 request signing on Gateway `/v1/process`
- **Policy Engine Integration**: Two-pass policy evaluation in gateway (pre-check + post-MARS check)
- **Privacy Budget Enforcement**: Per-query epsilon tracking with 429 rejection when exhausted
- **DPIA Auto-Trigger**: Fire-and-forget DPIA generation for high-risk requests (risk_tier <= 1)
- **Redis Persistence**: Optional Redis persistence for AuditLogger (`nss:audit:log`) and PrivacyBudgetTracker (`nss:privacy:budgets`) with graceful degradation
- **SAG Encryption**: AES-256-GCM encryption/decryption of vector payloads at rest (`sag_encryption.py`)
- **RAG Pipeline**: Full retrieval-augmented generation pipeline with encrypted document storage (`rag_pipeline.py`)
- **Tool Execution Endpoint**: `/v1/tools/execute` with VIGIL pre-check and sandbox isolation
- **Unlearning Orchestrator**: GDPR Art. 17 `/v1/unlearn/{user_id}` endpoint (budget reset + vector deletion)
- **Vector Retention Policy**: Automatic `created_at` timestamps on upsert; `cleanup_expired()` method (default 90 days)
- **Prometheus Metrics**: OpenMetrics text format export at `/metrics/prometheus`
- **TLS 1.3 Support**: Optional TLS configuration passthrough on all 4 servers
- **SHIELD Token Update**: Tokens now match White Paper format (`[END_OF_USER_INSTRUCTION] GUARDIAN_SHIELD_ACTIVE`)
- 46 new tests (209 total): security enforcement, persistence, SAG encryption, RAG pipeline, unlearning, vector retention

### Changed

- Gateway pipeline now includes full security chain: JWT → HMAC → Policy → Budget → PII → STEER → PNC → SENTINEL → MARS → Policy Post → DPIA → APEX → SHIELD → LLM → Budget Consume
- AuditLogger constructor accepts optional `redis_url` parameter
- PrivacyBudgetTracker constructor accepts optional `redis_url` parameter
- VectorStore `upsert()` auto-injects `created_at` timestamp; constructor accepts `retention_seconds`

## [3.1.1] - 2026-02-08

### Added

- Guardian Shield Security Layer with 5 components (MARS, APEX, SENTINEL, SHIELD, VIGIL)
- 6-Layer Defensive Architecture
- Enterprise White Paper with comprehensive documentation
- STRIDE Threat Model analysis (Score: 9.7/10)
- Penetration testing results (0 Critical findings)
- GDPR Compliance Matrix (98/100)
- EU AI Act Alignment documentation (96/100)
- ISO 27001 Alignment assessment (4.1/5)
- Dual-License Model (AGPL-3.0 + Commercial)
- Reference implementation with FastAPI Gateway
- Docker and Kubernetes deployment configuration
- CI/CD Pipelines (Markdown Lint, Spell Check, Security Scan, Python CI)
- GitHub Copilot Instructions
- Comprehensive documentation structure (architecture, security, compliance, deployment)

### Changed

- SLA target adjusted to 600ms (from 500ms) to reflect realistic p95 latency
- Updated LLaMA reference from v2 to v3
- Clarified cost savings metric: 66% refers to API costs, not total TCO
- Corrected per-user cost notation in comparison table

### Fixed

- License consistency (MIT -> AGPL-3.0 to match specification)
- GitHub repository URL references
- German language errors (Modifikationen, Gemeinschaftliche, hoechstes Risiko)
- GDPR compliance score consistency (98/100 throughout)
- Cloud Act / FISA Section 702 legal distinction

## [3.1.0] - 2026-01-15

### Added

- Initial NSS v3.1 specification
- SAG encryption architecture
- STEER transformation pipeline
- DPSparseVoteRAG implementation concept
- 5-domain architecture model
- Port schema design
