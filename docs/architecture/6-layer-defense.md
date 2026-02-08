# NSS v3.1.1 -- 6-Layer Defensive Architecture

[Back to Main Documentation](../README.md) | [Full White Paper](../white-paper/NSS-v3.1.1-Enterprise-White-Paper.md)

---

## Overview

NSS v3.1.1 implements a Defense-in-Depth strategy through a 6-Layer Defensive Architecture. Each layer addresses a specific category of risk, and together they achieve an overall Attack Success Rate (ASR) of less than 1%.

---

## Architecture Diagram

```
+------------------------------------------------+
| LAYER 5: GOVERNANCE PLANE (Port 11339)         |
| - Policy Engine (OPA)                          |
| - Privacy Budget (epsilon-tracking)            |
| - Cost Budget (EUR)                            |
| - DPIA Generator                               |
| - Unlearning Orchestrator                      |
| RISK REDUCTION: -20% compliance-related        |
+------------------------+-----------------------+
                         |
                         v
+------------------------------------------------+
| LAYER 4: GUARDIAN SHIELD (Port 11338)          |
| - MARS (Mistral Risk Scorer)                   |
| - APEX (Adaptive Path Evaluator)               |
| - SENTINEL (Injection Defense)                 |
| - SHIELD (Defensive Tokens)                    |
| - VIGIL (Tool Safety)                          |
| RISK REDUCTION: -85% (ASR < 1%)               |
+------------------------+-----------------------+
                         |
                         v
+------------------------------------------------+
| LAYER 3: COGNITIVE GATEWAY (Port 11337)        |
| - PII Redaction (Regex + ML)                   |
| - STEER Transformation                         |
| - PNC Compression                              |
| - Request Signing (HMAC)                       |
| RISK REDUCTION: -45% (data exposure)           |
+------------------------+-----------------------+
                         |
                         v
+------------------------------------------------+
| LAYER 2: AGENT EXECUTION                       |
| - DPSparseVoteRAG (DP + Voting)                |
| - Tool Isolation (WASM/WASI)                   |
| - VIGIL Validation                             |
| - Error Handling                               |
| RISK REDUCTION: -30% (execution errors)        |
+------------------------+-----------------------+
                         |
                         v
+------------------------------------------------+
| LAYER 1: KNOWLEDGE FABRIC (Port 6333)          |
| - Qdrant Vector DB (SAG Encrypted)             |
| - Embedding Model (all-MiniLM-L6-v2)           |
| - Metadata Encryption                          |
| - Retention Policy                             |
| RISK REDUCTION: -50% (unauthorized access)     |
+------------------------------------------------+
```

---

## Layer Descriptions

### Layer 5: Governance Plane (Port 11339)

The top-level control layer responsible for policy enforcement, privacy budget tracking, cost governance, and automated compliance reporting. It uses Open Policy Agent (OPA) for policy-as-code and includes the Unlearning Orchestrator for GDPR Art. 17 (Right to Erasure) compliance. Reduces compliance-related risk by 20%.

### Layer 4: Guardian Shield (Port 11338)

The core security layer containing five specialized components: MARS (risk scoring), APEX (cost-optimized routing), SENTINEL (injection defense), SHIELD (defensive token injection), and VIGIL (tool call safety). This layer is responsible for the largest single risk reduction at 85%, bringing the ASR below 1%. See the [Guardian Shield documentation](guardian-shield.md) for full details.

### Layer 3: Cognitive Gateway (Port 11337)

The only externally accessible layer. It handles PII redaction using a combination of regex and ML-based detection, applies STEER transformations for prompt normalization, compresses payloads via PNC, and signs all requests with HMAC-SHA256. Reduces data exposure risk by 45%.

### Layer 2: Agent Execution

Handles the actual AI model invocation and tool execution. Uses DPSparseVoteRAG for differentially private retrieval-augmented generation with voting consensus, isolates tool execution in WASM/WASI sandboxes, and validates all tool calls through VIGIL. Reduces execution error risk by 30%.

### Layer 1: Knowledge Fabric (Port 6333)

The foundational data layer built on Qdrant Vector DB with SAG (Sovereign Authentication Gateway) encryption. All embeddings are generated using the all-MiniLM-L6-v2 model. Metadata is encrypted at rest, and retention policies are enforced automatically. Reduces unauthorized access risk by 50%.

---

## Attack Vectors and Mitigations

| Attack Vector | OWASP Reference | Mitigation | Layer | Effectiveness |
|---|---|---|---|---|
| Prompt Injection | A03:2021 | SENTINEL (3/3 consensus) | Layer 4 | 98% |
| Data Exfiltration | A01:2021 | PII-Redaction + TEE | Layer 3 + 1 | 99% |
| Unauthorized Tool Use | A05:2021 | VIGIL (CIA) | Layer 4 | 97% |
| Model Poisoning | A08:2023 | DPSparseVote + Anomaly | Layer 2 | 95% |
| Privacy Leakage | Custom | Differential Privacy | Layer 2 + 5 | 96% |
| Denial of Service | A06:2021 | Rate Limiting (VIGIL) | Layer 4 | 92% |
| Timing Attacks | Custom | Constant-Time Ops | Layer 1 | 94% |

**Average Attack Success Rate (ASR): < 1%**

---

## Latency Budget (p95, Single Request)

| Layer | Latency | Breakdown |
|---|---|---|
| Guardian Shield | 80ms | MARS 15ms, APEX 3ms, SENTINEL 40ms, SHIELD 2ms, VIGIL 20ms |
| Cognitive Gateway | 150ms | PII Redaction 60ms, STEER 40ms, PNC 30ms, Signing 20ms |
| Agent Execution | 200ms | DPSparseVote 100ms, Tool Invoke 60ms, Error Handling 40ms |
| Knowledge Fabric | 100ms | Vector Search (Qdrant) |
| **Total** | **530ms** | SLA target: < 600ms |

---

## References

- [Guardian Shield Detail](guardian-shield.md)
- [Port Schema](port-schema.md)
- [STRIDE Threat Model](../security/stride-threat-model.md)
- [Full White Paper](../white-paper/NSS-v3.1.1-Enterprise-White-Paper.md)
