# ADR-004: 6-Layer Defensive Architecture

## Status

Accepted

## Context

NSS needs an architecture that provides defense-in-depth for AI workloads while maintaining clear separation of concerns, independent scalability, and regulatory traceability.

## Decision

Implement a 6-layer architecture with strict isolation boundaries:

1. **Knowledge Fabric** (Layer 1) -- Vector storage, embeddings, SAG encryption
2. **Agent Execution** (Layer 2) -- DP-augmented RAG, tool sandbox
3. **Cognitive Gateway** (Layer 3) -- PII redaction, STEER, PNC, HMAC, pipeline orchestration
4. **Guardian Shield** (Layer 4) -- MARS, SENTINEL, APEX, SHIELD, VIGIL
5. **Governance Plane** (Layer 5) -- Policy engine, privacy budget, DPIA, audit
6. **Cross-Cutting** -- JWT auth, metrics, middleware, caching

## Rationale

- **Defense-in-depth**: Each layer adds independent security controls; compromise of one layer does not bypass others
- **Regulatory mapping**: Each layer maps to specific GDPR/EU AI Act requirements for audit trails
- **Independent scaling**: Microservice boundaries allow scaling Guardian Shield independently of Gateway
- **Clear responsibility**: Each component has a single, well-defined responsibility
- **Testability**: Layer isolation enables comprehensive unit and integration testing (209 tests)

## Alternatives Considered

- **Monolithic application**: Simpler but no isolation; single point of failure; harder to scale
- **3-tier architecture**: Too coarse; insufficient separation for security and governance concerns
- **Event-driven/CQRS**: Adds complexity without clear benefit for synchronous request/response AI workloads
- **Service mesh**: Overhead of sidecar proxies not justified for reference implementation

## Consequences

- 4 separate FastAPI microservices (ports 11337-11340) plus Qdrant (6333)
- Inter-service communication via HTTP (internal loopback)
- Higher operational complexity than a monolith
- Docker Compose required for full-stack deployment
