# NSS Project - GitHub Copilot Instructions

## Project Overview

NSS (Nexus Sovereign Standard) v3.1.1 is a sovereign, GDPR-compliant AI infrastructure standard for the EU. The system uses a 6-Layer Defensive Architecture with Guardian Shield.

## LLM Stack

- **Models:** Mistral AI (Mistral-7B-Instruct-v0.3 for fast tasks, Mistral-Nemo-12B for complex tasks)
- **Runtime:** Ollama (local inference server, no cloud API calls)
- **Embeddings:** all-MiniLM-L6-v2 via sentence-transformers

## Architecture

- Layer 5: Governance Plane (Port 11339) - OPA, Privacy Budget, DPIA
- Layer 4: Guardian Shield (Port 11338) - MARS, APEX, SENTINEL, SHIELD, VIGIL
- Layer 3: Cognitive Gateway (Port 11337) - PII Redaction, STEER, HMAC
- Layer 2: Agent Execution - DPSparseVoteRAG, WASM/WASI isolation
- Layer 1: Knowledge Fabric (Port 6333) - Qdrant, Embeddings

## Coding Standards

- Python 3.11+ required
- Framework: FastAPI for all HTTP services
- Linting: ruff (replaces flake8/isort/black)
- Type checking: mypy (strict mode)
- Docstrings: Google style
- All functions require type hints
- No hardcoded secrets - use environment variables with NSS_ prefix

## Security Requirements (CRITICAL)

- NEVER log PII (Personally Identifiable Information)
- All data at rest: SAG encryption (AES-256-GCM)
- All data in transit: TLS 1.3
- API authentication: HMAC-SHA256 request signing
- JWT tokens: 15 minute max lifetime
- All tool calls must pass VIGIL CIA checks
- Differential privacy: epsilon tracking for all data aggregation
- Network: loopback binding only (127.0.0.1), no 0.0.0.0

## GDPR Compliance

- Privacy by Design required for all features
- PII redaction before any data processing
- Art. 17 support (right to be forgotten) via Unlearning Orchestrator
- Privacy tiers (0-3) must be respected
- All data processing must be logged in audit trail

## Testing

- Minimum coverage: 80%
- Security tests for all Guardian Shield components
- OWASP TOP 10 regression tests for SENTINEL
- Performance benchmarks for latency budget
- Use pytest with fixtures in conftest.py

## Naming Conventions

- Components: UPPERCASE acronyms (MARS, APEX, SENTINEL, SHIELD, VIGIL)
- Python modules: snake_case
- Config files: kebab-case
- Environment variables: NSS_ prefix + SCREAMING_SNAKE_CASE
- Docker images: nss/{component}:{version}

## Commit Convention

Use Conventional Commits:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `security:` security improvement
- `test:` testing
- `refactor:` code refactoring
- `ci:` CI/CD changes
- `chore:` maintenance

## Key Dependencies

- FastAPI + uvicorn (HTTP server)
- Pydantic v2 (data validation)
- ollama (LLM client)
- qdrant-client (vector DB)
- sentence-transformers (embeddings)
- redis (caching)
- cryptography (AES-256-GCM, HMAC)
- PyJWT (JWT handling)
- structlog (structured logging)
