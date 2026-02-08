# NSS v3.1.1 -- Scaling Guide

[Back to Main Documentation](../README.md) | [Full White Paper](../white-paper/NSS-v3.1.1-Enterprise-White-Paper.md)

---

## Overview

NSS v3.1.1 scales horizontally with near-linear throughput gains. This guide covers single-instance specifications, multi-instance scaling, cost analysis, and auto-scaling recommendations.

---

## Single Instance Specifications

| Resource | Specification |
|---|---|
| Throughput | 2,500 RPS |
| Latency (p95) | 530ms |
| GPU | 1x NVIDIA A100 (40GB) |
| CPU | 16 vCores |
| RAM | 64GB |
| SLA Target | < 600ms |

---

## Horizontal Scaling

### 3x Instances (Recommended Starting Point)

| Metric | Value |
|---|---|
| Throughput | 7,500 RPS (+200%) |
| Latency (p95) | 540ms (stable) |
| Infrastructure Cost | 3x single instance |

With load balancing across 3 instances, throughput scales linearly while latency remains stable. This is the recommended minimum for production deployments.

### 10x Instances (Enterprise Scale)

| Metric | Value |
|---|---|
| Throughput | 25,000 RPS |
| Latency (p95) | 560ms (+30ms degradation) |
| Infrastructure Cost | 10x single instance + load balancer |

At 10 instances, a minor 30ms latency degradation occurs due to load balancer overhead and inter-instance coordination. This remains well within the 600ms SLA.

---

## Scaling Summary

| Configuration | Instances | Throughput | Latency (p95) | Monthly Infra Cost |
|---|---|---|---|---|
| Minimal | 1 | 2,500 RPS | 530ms | 300 EUR |
| Production | 3 | 7,500 RPS | 540ms | 800 EUR |
| Enterprise | 10 | 25,000 RPS | 560ms | 2,000 EUR |

---

## Cost Scaling Analysis

### API Cost by Volume (Mistral Small Model)

| Monthly Requests | API Cost | Cost per Request |
|---|---|---|
| 100K | 100 EUR | 0.001 EUR |
| 500K | 300 EUR | 0.0006 EUR |
| 1M | 500 EUR | 0.0005 EUR |
| 5M | 2,000 EUR | 0.0004 EUR (volume discount) |
| 10M | 3,500 EUR | 0.00035 EUR |

### Total Cost Example (1M requests/month, 3 instances)

| Component | Cost |
|---|---|
| API costs | 500 EUR |
| Infrastructure (3 instances) | 800 EUR |
| **Total** | **1,300 EUR/month** |

**Comparison:** OpenAI at equivalent volume costs approximately 1,663 EUR/month, making NSS 21% cheaper with full GDPR compliance and no Cloud Act risk.

---

## Auto-Scaling Recommendations

### Horizontal Pod Autoscaler (Kubernetes)

```bash
kubectl autoscale deployment nss-guardian-shield \
  --namespace ai-infrastructure \
  --min=3 --max=10 \
  --cpu-percent=70
```

**Recommended Configuration:**

| Parameter | Value | Rationale |
|---|---|---|
| Minimum replicas | 3 | High availability baseline |
| Maximum replicas | 10 | Enterprise-scale ceiling |
| Scale-up trigger | CPU > 70% | Prevents latency degradation |
| Scale-down trigger | CPU < 30% | Cost optimization |
| Cooldown period | 5 minutes | Prevents flapping |

### Scaling Strategy

1. **Start with 3 instances** for production readiness and high availability.
2. **Monitor p95 latency** -- if it approaches 580ms, scale up.
3. **Auto-scale to 5--10 instances** during peak traffic periods.
4. **Scale down during off-peak** to reduce infrastructure costs.

### Custom Metrics Scaling

For more precise scaling, use MARS throughput as a custom metric:

- Scale up when MARS throughput per instance exceeds 2,000 RPS (80% capacity)
- Scale down when MARS throughput per instance drops below 750 RPS (30% capacity)

---

## Performance Optimization

For workloads requiring latency below 300ms (target for v3.2):

- **Caching layer (Redis):** Reduces latency by approximately 70% for repeated queries (target: 150ms)
- **Model quantization (Mistral-Q4):** Reduces MARS latency by approximately 20%
- **Both combined:** Target p95 of 150ms for cached queries

---

## References

- [Kubernetes Deployment Guide](kubernetes-guide.md)
- [Migration from OpenAI](migration-from-openai.md)
- [6-Layer Defense Architecture](../architecture/6-layer-defense.md)
- [Full White Paper](../white-paper/NSS-v3.1.1-Enterprise-White-Paper.md)
