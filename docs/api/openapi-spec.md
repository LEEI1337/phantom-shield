# NSS v3.1.1 API Reference

All NSS endpoints require JWT authentication (except `/health`, `/metrics`, and `/metrics/prometheus`).

## Authentication

All `/v1/*` endpoints require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer <JWT_TOKEN>
```

Tokens use HS256 signing with 15-minute expiry. Generate tokens via `nss.auth.create_token()`.

The Gateway `/v1/process` endpoint additionally requires HMAC-SHA256 request signing:

```
X-HMAC-Signature: <HMAC_SHA256_SIGNATURE>
X-HMAC-Timestamp: <UNIX_TIMESTAMP>
X-HMAC-Nonce: <UUID4>
```

---

## Cognitive Gateway `:11337`

### `GET /health`

Liveness/readiness probe. No authentication required.

**Response** `200 OK`

```json
{"status": "healthy", "service": "nss-gateway", "version": "3.1.1"}
```

### `POST /v1/process`

Full 6-layer processing pipeline. Requires JWT + HMAC.

**Request Body** (`application/json`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | yes | Unique user identifier |
| `message` | string | yes | User input text |
| `privacy_tier` | integer | no | Privacy level 0-3 (default 2) |
| `role` | string | no | User role (default "viewer") |

**Response** `200 OK`

```json
{
  "response": "LLM-generated response text",
  "trace_id": "uuid4",
  "risk_score": {"score": 0.15, "tier": 3, "label": "LOW"},
  "model_used": "mistral:7b-instruct-v0.3",
  "pii_entities_found": 2,
  "cached": false
}
```

**Error Responses**

- `401 Unauthorized` -- Missing/invalid JWT or HMAC signature
- `403 Forbidden` -- Policy engine denied the request (role/tier mismatch)
- `429 Too Many Requests` -- Privacy budget exhausted for this user

### `POST /v1/tools/execute`

Execute a registered tool in the WASM/WASI sandbox with VIGIL pre-check.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool_name` | string | yes | Name of the registered tool |
| `args` | object | no | Arguments to pass to the tool |
| `user_id` | string | yes | Requesting user identifier |
| `timeout` | float | no | Timeout in seconds (default 5.0) |

**Response** `200 OK`

```json
{
  "output": "tool execution result",
  "vigil_verdict": "ALLOW",
  "execution_time_ms": 42.5,
  "sandbox_metadata": {"tool": "calculator", "isolated": true}
}
```

### `POST /v1/unlearn/{user_id}`

GDPR Article 17 right-to-be-forgotten orchestrator. Resets privacy budget, deletes vectors, logs audit event.

**Response** `200 OK`

```json
{
  "user_id": "user-1",
  "actions": {
    "budget_reset": true,
    "audit_logged": true,
    "vectors_deleted": true,
    "cache_note": "Cache entries expire within 5 minutes (TTL=300s)"
  }
}
```

---

## Guardian Shield `:11338`

### `POST /v1/mars/score`

MARS risk scoring via LLM-assisted evaluation.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | yes | Text to evaluate for risk |
| `user_id` | string | no | User context for scoring |

**Response** `200 OK`

```json
{"score": 0.35, "tier": 2, "label": "MEDIUM"}
```

### `POST /v1/sentinel/check`

SENTINEL 3-method prompt injection defense.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | yes | Text to check for injection attacks |

**Response** `200 OK`

```json
{
  "safe": true,
  "methods": {
    "rule_based": {"triggered": false, "patterns": []},
    "llm_based": {"triggered": false},
    "embedding": {"triggered": false, "similarity": 0.12}
  }
}
```

### `POST /v1/apex/route`

APEX intelligent model routing based on query complexity.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | yes | Query to route |
| `confidence` | float | no | Confidence threshold for routing |

**Response** `200 OK`

```json
{"model": "mistral:7b-instruct-v0.3", "tier": "standard", "reason": "confidence_above_threshold"}
```

### `POST /v1/shield/enhance`

SHIELD defensive token wrapping.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | yes | User prompt to wrap with defensive tokens |
| `system_prompt` | string | no | Additional system context |

**Response** `200 OK`

```json
{"enhanced_prompt": "[END_OF_USER_INSTRUCTION] GUARDIAN_SHIELD_ACTIVE..."}
```

### `POST /v1/vigil/check`

VIGIL tool-call CIA (Confidentiality, Integrity, Availability) validation.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool_name` | string | yes | Tool to validate |
| `args` | object | yes | Tool arguments |
| `user_id` | string | yes | Requesting user |

**Response** `200 OK`

```json
{"verdict": "ALLOW", "reasons": []}
```

---

## Governance Plane `:11339`

### `POST /v1/policy/evaluate`

OPA-style policy evaluation for access control decisions.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | string | yes | User role (admin/data_processor/auditor/viewer) |
| `pii_detected` | boolean | no | Whether PII was found in request |
| `privacy_tier` | integer | no | Privacy tier 0-3 |
| `risk_tier` | integer | no | Risk tier 0-3 |

**Response** `200 OK`

```json
{"allowed": true, "reasons": [], "evaluated_rules": 3}
```

### `GET /v1/privacy/budget/{user_id}`

Get remaining differential privacy epsilon budget.

**Response** `200 OK`

```json
{"user_id": "user-1", "remaining": 0.7, "total": 1.0}
```

### `POST /v1/privacy/consume`

Consume epsilon from a user's privacy budget.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | yes | Target user |
| `epsilon` | float | yes | Amount to consume |

**Response** `200 OK`

```json
{"consumed": true, "remaining": 0.6}
```

### `POST /v1/dpia/generate`

Generate a GDPR Article 35 Data Protection Impact Assessment report.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `processing_activity` | string | yes | Description of data processing |
| `data_categories` | list[string] | yes | Types of data involved |
| `risk_tier` | integer | yes | Risk classification 0-3 |

**Response** `200 OK`

```json
{
  "report": "# DPIA Report\n\n## 1. Processing Description...",
  "sections": 5,
  "risk_level": "MEDIUM"
}
```

### `GET /v1/audit/{audit_id}`

Retrieve a specific audit trail entry by ID.

### `GET /v1/audit`

Retrieve the full audit trail with hash-chain integrity.

---

## Metrics Server `:11340`

### `GET /metrics`

Full metrics snapshot in JSON format. No authentication required.

**Response** `200 OK`

```json
{
  "counters": {
    "nss_requests_total": 142,
    "nss_requests_blocked": 3,
    "nss_pii_entities_redacted": 27,
    "nss_privacy_budget_consumed": 15
  },
  "histograms": {
    "nss_request_latency_ms": {"count": 142, "sum": 8540.5, "avg": 60.14},
    "nss_guardian_latency_ms": {"count": 142, "sum": 2130.2, "avg": 15.0}
  }
}
```

### `GET /metrics/prometheus`

Prometheus/OpenMetrics text format export. No authentication required.

**Response** `200 OK` (`text/plain; version=0.0.4`)

```
# HELP nss_requests_total Total number of requests processed
# TYPE nss_requests_total counter
nss_requests_total 142
# HELP nss_request_latency_ms Request latency in milliseconds
# TYPE nss_request_latency_ms histogram
nss_request_latency_ms_count 142
nss_request_latency_ms_sum 8540.5
```

---

## FastAPI Auto-Generated Docs

Each service also exposes interactive API documentation (no auth required):

- Gateway: `http://localhost:11337/docs` (Swagger UI)
- Guardian: `http://localhost:11338/docs`
- Governance: `http://localhost:11339/docs`
- Metrics: `http://localhost:11340/docs`
