# NSS v3.1.1 -- Port Schema

[Back to Main Documentation](../../README.md) | [Full White Paper](../white-paper/NSS-v3.1.1-Enterprise-White-Paper.md)

---

## Overview

NSS uses a dedicated port schema in the 113XX range (a nod to "LEET") with strict network isolation. Only one port is externally accessible; all other services are bound to the loopback interface.

---

## Port Assignments

| Port | Service | Access Level | Description |
|---|---|---|---|
| **11337** | Cognitive Gateway | **External** (only external port) | Entry point for all API requests. Handles PII redaction, STEER transformation, PNC compression, and HMAC request signing. |
| **11338** | Guardian Shield | Internal only | Core security layer. Hosts MARS, APEX, SENTINEL, SHIELD, and VIGIL components. |
| **11339** | Governance Plane | Internal only | Policy engine (OPA), privacy budget tracking, DPIA generation, and audit trail. |
| **11340** | Metrics | Internal only | Monitoring and observability endpoint for real-time metrics collection. |
| **6333** | Qdrant Vector DB | Internal only | Knowledge Fabric layer. SAG-encrypted vector storage for RAG operations. |

---

## API Endpoints per Service

### Cognitive Gateway (`:11337`)

| Method | Endpoint | Request Body | Description |
|--------|----------|-------------|-------------|
| `GET` | `/health` | -- | Liveness/readiness probe |
| `GET` | `/metrics` | -- | Basic operational metrics (requests, latency, blocked) |
| `POST` | `/v1/process` | `NSSRequest` | Full 6-layer pipeline: PII -> SENTINEL -> MARS -> APEX -> SHIELD -> LLM |

**NSSRequest schema:**
```json
{
  "user_id": "string",
  "message": "string",
  "privacy_tier": 0,
  "metadata": {}
}
```

### Guardian Shield (`:11338`)

| Method | Endpoint | Request Body | Description |
|--------|----------|-------------|-------------|
| `GET` | `/health` | -- | Service health check |
| `POST` | `/v1/mars/score` | `{"text": "...", "language": "de"}` | MARS risk scoring (score 0-1, tier 0-3) |
| `POST` | `/v1/sentinel/check` | `{"text": "..."}` | SENTINEL 3-method injection defense (rules + LLM + embedding) |
| `POST` | `/v1/apex/route` | `{"query": "...", "confidence": 0.9, "budget_remaining": 1.0}` | APEX intelligent model routing |
| `POST` | `/v1/shield/enhance` | `{"prompt": "..."}` | SHIELD defensive token wrapping |
| `POST` | `/v1/vigil/check` | `{"tool_name": "...", "args": {}, "user_id": "..."}` | VIGIL tool-call CIA validation |

### Governance Plane (`:11339`)

| Method | Endpoint | Request Body | Description |
|--------|----------|-------------|-------------|
| `GET` | `/health` | -- | Service health check |
| `POST` | `/v1/policy/evaluate` | `{"role": "viewer", "risk_tier": null, "pii_detected": false, "privacy_tier": 0, "tool_name": null}` | OPA-style policy evaluation |
| `GET` | `/v1/privacy/budget/{user_id}` | -- | Remaining epsilon budget for user |
| `POST` | `/v1/privacy/consume` | `{"epsilon": 0.1, "user_id": "..."}` | Consume epsilon from privacy budget |
| `POST` | `/v1/dpia/generate` | `{"processing_activity": "...", "data_categories": [...], "risk_tier": 3, "privacy_budget_remaining": 1.0}` | Generate GDPR Art. 35 DPIA report |
| `GET` | `/v1/audit/{audit_id}` | -- | Retrieve specific audit trail entry |
| `GET` | `/v1/audit` | -- | Retrieve all audit trail entries |

### Metrics Server (`:11340`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `GET` | `/metrics` | Full metrics snapshot (counters + histograms) |

**Metrics response schema:**
```json
{
  "timestamp": 1707400000,
  "counters": {
    "nss_requests_total": 0,
    "nss_requests_blocked": 0,
    "nss_pii_entities_redacted": 0,
    "nss_privacy_budget_consumed": 0
  },
  "histograms": {
    "nss_request_latency_ms": {"count": 0, "sum": 0, "min": 0, "max": 0, "avg": 0},
    "nss_guardian_latency_ms": {"count": 0, "sum": 0, "min": 0, "max": 0, "avg": 0}
  }
}
```

---

## Network Isolation

All internal ports are bound exclusively to the loopback interface (`127.0.0.1` / `lo`), creating an air-gapped internal network. Even Port 11337 (Gateway) is blocked from external access by default and must be explicitly allowed through firewall configuration.

**Network Isolation Level: Air-Gapped (Loopback)**

---

## Firewall Rules

```bash
# Block external access to the Gateway by default
-A INPUT -p tcp --dport 11337 -j DROP

# Allow loopback access only
-A INPUT -i lo -p tcp --dport 11337 -j ACCEPT

# Block all forwarding to NSS ports from external interfaces
-A FORWARD -i eth0 -p tcp --dport 113XX -j DROP
```

### Explanation

1. **Default deny**: All incoming TCP traffic to Port 11337 is dropped. This prevents any external host from reaching the Gateway without explicit allowlisting.

2. **Loopback allow**: Traffic originating from the loopback interface (`lo`) is permitted. This means only processes running on the same host (or within the same Kubernetes pod network, when configured) can reach the Gateway.

3. **Forward block**: Forwarding from external network interfaces (e.g., `eth0`) to any port in the 113XX range is explicitly blocked. This prevents routing or NAT-based access to internal services.

---

## Deployment Considerations

- In a **Kubernetes** deployment, inter-pod communication replaces loopback binding. Use Kubernetes NetworkPolicies to enforce equivalent isolation.
- The **Qdrant** port (6333) uses the standard Qdrant default but is restricted to loopback to prevent unauthorized vector database access.
- **Metrics** (Port 11340) should be exposed to your monitoring stack (e.g., Prometheus) through a secure internal network or service mesh, not through public ingress.

---

## References

- [6-Layer Defense Architecture](6-layer-defense.md)
- [Guardian Shield Detail](guardian-shield.md)
- [Kubernetes Deployment Guide](../deployment/kubernetes-guide.md)
- [Full White Paper](../white-paper/NSS-v3.1.1-Enterprise-White-Paper.md)
