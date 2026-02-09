# ADR-005: HMAC-SHA256 Request Signing

## Status

Accepted

## Context

NSS needs request integrity verification to prevent tampering between services and ensure non-repudiation of API calls. JWT alone authenticates identity but does not verify request body integrity.

## Decision

Use HMAC-SHA256 request signing with timestamp-based replay protection on the Gateway `/v1/process` endpoint.

## Rationale

- **Body integrity**: HMAC covers the full request body; any modification invalidates the signature
- **Replay protection**: Timestamp + nonce headers prevent replay attacks (5-minute window)
- **Lightweight**: No PKI infrastructure required; shared secret is sufficient for internal services
- **Non-repudiation**: Combined with JWT identity, HMAC provides full request attribution
- **FastAPI Dependency pattern**: Implemented as `Depends(verify_hmac)` rather than middleware, because Starlette middleware can only read the request body once

## Implementation

```
X-HMAC-Signature: HMAC-SHA256(secret, timestamp + nonce + body)
X-HMAC-Timestamp: <unix_timestamp>
X-HMAC-Nonce: <uuid4>
```

The signature is verified before any pipeline processing begins.

## Alternatives Considered

- **JWT claims only**: Does not verify body integrity; subject to body swapping attacks
- **mTLS**: Heavyweight; requires certificate management infrastructure
- **AWS SigV4**: Over-engineered for internal service communication
- **Starlette middleware**: Body can only be read once in Starlette, causing downstream failures

## Consequences

- All clients must compute HMAC signature before sending requests
- Shared secret must be distributed securely to all services
- Clock synchronization required between services (5-minute tolerance)
- Additional latency for signature computation and verification (negligible, < 1ms)
