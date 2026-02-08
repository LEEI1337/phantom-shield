# NSS v3.1.1 -- Port Schema

[Back to Main Documentation](../README.md) | [Full White Paper](../white-paper/NSS-v3.1.1-Enterprise-White-Paper.md)

---

## Overview

NSS uses a dedicated port schema in the 113XX range (a nod to "LEET") with strict network isolation. Only one port is externally accessible; all other services are bound to the loopback interface.

---

## Port Assignments

| Port | Service | Access Level | Description |
|---|---|---|---|
| **11337** | Cognitive Gateway | **External** (only external port) | Entry point for all API requests. Handles PII redaction, STEER transformation, PNC compression, and HMAC request signing. |
| **11338** | Guardian Shield | Internal only | Core security layer. Hosts MARS, APEX, SENTINEL, SHIELD, and VIGIL components. |
| **11339** | Governance Plane | Internal only | Policy engine (OPA), privacy budget tracking, cost budgets, DPIA generation, and Unlearning Orchestrator. |
| **11340** | Metrics | Internal only | Monitoring and observability endpoint for real-time metrics collection. |
| **6333** | Qdrant Vector DB | Internal only | Knowledge Fabric layer. SAG-encrypted vector storage for RAG operations. |

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
