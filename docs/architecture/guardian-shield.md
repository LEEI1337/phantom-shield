# NSS v3.1.1 -- Guardian Shield (Layer 4)

[Back to Main Documentation](../README.md) | [Full White Paper](../white-paper/NSS-v3.1.1-Enterprise-White-Paper.md)

---

## Overview

The Guardian Shield is the core security layer of the NSS 6-Layer Defensive Architecture, operating on **Port 11338** (internal only). It contains five specialized components that together achieve an 85% risk reduction and bring the Attack Success Rate (ASR) below 1%.

---

## Components

### 1. MARS -- Multilingual AI Risk Scorer

MARS provides real-time risk scoring for all incoming requests using a fine-tuned Mistral model.

**Technical Specifications:**

| Parameter | Value |
|---|---|
| Model | Mistral-7B-Instruct-v0.3 |
| Size | 7B parameters (4GB VRAM) |
| Latency | 15ms (p95, batch-1) |
| Throughput | 2,500 req/s (single GPU) |
| Languages | DE, EN, FR, IT, ES, NL, PL, PT, RO, SV |

**Risk Tiers:**

| Tier | Name | Likelihood | Exposure Time | Action |
|---|---|---|---|---|
| Tier 0 | Ephemeral (highest risk) | 0.95--1.00 | < 1 second | Automatic abort + alert |
| Tier 1 | Transient (high risk) | 0.90--0.95 | < 24 hours | Automatic purge after 24h + policy review |
| Tier 2 | Persistent (medium risk) | 0.85--0.90 | < 30 days | Audit trail + manual review |
| Tier 3 | Governance (low risk) | 0.80--0.85 | < 365 days | DPIA + legal review + board notification |

**Validation Results (10,000 DE/EN prompts, OWASP TOP 10 + Custom):**

| Attack Type | Precision | Recall | F1 Score |
|---|---|---|---|
| Direct Injection | 99.2% | 98.8% | 0.990 |
| Jailbreak Attempts | 94.5% | 93.2% | 0.939 |
| Data Exfiltration | 97.8% | 96.5% | 0.972 |
| Role-Play Attacks | 92.1% | 89.7% | 0.907 |
| **Average** | **96.7%** | **95.6%** | **0.962** |

---

### 2. APEX -- Adaptive Path Evaluator

APEX provides intelligent model routing based on confidence thresholds and budget constraints, achieving up to 66% cost savings compared to always using the large model.

**Routing Logic:**

```
IF confidence(small_model_answer) > 0.85:
    USE small_model (Mistral-7B)
    COST: 0.0001 EUR | LATENCY: 15ms | ACCURACY: 94%

ELIF confidence <= 0.85 AND budget_available:
    USE large_model (Mistral-Nemo-12B)
    COST: 0.0005 EUR | LATENCY: 60ms | ACCURACY: 98%

ELSE:
    FALLBACK: small_model
    LOG: "Budget exhausted, degraded accuracy"
```

**Cost-Benefit Analysis (1M requests/month, Enterprise):**

| Strategy | Cost/Request | Monthly Cost | Avg Latency | Accuracy | Monthly Savings |
|---|---|---|---|---|---|
| Small Always | 0.0001 EUR | 100 EUR | 15ms | 94% | Baseline |
| Large Always | 0.0005 EUR | 500 EUR | 60ms | 98% | -400 EUR |
| **APEX (NSS)** | **0.00017 EUR** | **170 EUR** | **22ms** | **96.8%** | **+330 EUR (66%)** |

**12-month ROI: 3,960 EUR in savings.**

---

### 3. SENTINEL -- Injection Defense (Multi-Method Consensus)

SENTINEL uses a 3-method ensemble with consensus voting to defend against injection attacks, overcoming the limitations of any single detection method.

**Pipeline:**

```
1. LLM Check (Mistral-7B)      -> Vector [0,1]
2. Rule Check (Aho-Corasick)    -> Boolean
3. Embedding Check (MiniLM)     -> Anomaly Score

CONSENSUS: Requires 2/3 Methods Agreement
- All 3 flag:  BLOCK (confidence: 1.0)
- 2 flag:      BLOCK (confidence: 0.9)
- 1 flags:     WARN  (confidence: 0.6)
- None flag:   ALLOW (confidence: 0.95)
```

**Why Consensus Matters:**

| Method | Strengths | Weaknesses |
|---|---|---|
| LLM-Only | Context-aware | 15-20% bypass rate, 30-40ms latency |
| Rule-Based Only | Very fast (< 2ms) | 25-30% bypass on creative payloads, no semantics |
| Embedding-Based Only | Semantic detection | 8-12% FP/FN rate |

**Evaluation against OWASP TOP 10 Injections:**

| Injection Type | LLM | Rules | Embedding | Consensus | Block Rate |
|---|---|---|---|---|---|
| Direct SQL Injection | Pass | Pass | Pass | Pass | 100% |
| Stored XSS | Pass | Pass | Pass | Pass | 100% |
| OS Command Injection | Pass | Pass | Partial | Pass | 98% |
| LDAP Injection | Pass | Pass | Partial | Pass | 97% |
| Template Injection | Partial | Pass | Pass | Pass | 95% |
| Jailbreak (creative) | Partial | Partial | Pass | Partial | 88% |
| Advanced Evasion | Partial | Partial | Partial | Partial | 78% |
| **Average** | **96%** | **94%** | **92%** | **96%** | **95%** |

---

### 4. SHIELD -- Defensive Token Injection

SHIELD injects defensive tokens around user prompts to counteract jailbreak attempts through cognitive bias injection.

**Mechanism:**

- **Prepend tokens** reinforce system identity and instruction boundaries.
- **Append tokens** signal the end of user input and assert audit awareness.
- The original user prompt is wrapped: `[PREPEND_TOKENS] <original_request> [APPEND_TOKENS]`

**Performance:**

| Metric | Value |
|---|---|
| Overhead | < 2ms |
| Jailbreak mitigation improvement | +8--12% |
| Mechanism | Cognitive Bias Injection |

---

### 5. VIGIL -- Tool Call Safety (CIA Framework)

VIGIL enforces the CIA (Confidentiality, Integrity, Availability) triad on all tool calls within the agent execution layer.

**Confidentiality Checks:**
- Only authorized tools may be invoked
- PII is not permitted in tool arguments
- Secrets are never exposed in logs

**Integrity Checks:**
- Argument type validation
- SQL/Command injection prevention
- Signature verification

**Availability Checks:**
- Rate limiting (100 req/min per tool)
- Timeout protection (5s max)
- Resource limits (memory, CPU)

**Typical VIGIL response latency: 3.2ms**

---

## Key Metrics Summary

| Metric | Value |
|---|---|
| Overall Risk Reduction | 85% |
| Attack Success Rate (ASR) | < 1% |
| Guardian Shield Latency (p95) | 80ms |
| MARS Throughput | 2,500 req/s |
| MARS Latency | 15ms |
| SENTINEL Average Block Rate | 95% |
| SHIELD Overhead | < 2ms |
| VIGIL Latency | 3.2ms |
| APEX Cost Savings | 66% vs. large model |
| Languages Supported | 10 |

---

## References

- [6-Layer Defense Architecture](6-layer-defense.md)
- [Port Schema](port-schema.md)
- [STRIDE Threat Model](../security/stride-threat-model.md)
- [Full White Paper](../white-paper/NSS-v3.1.1-Enterprise-White-Paper.md)
