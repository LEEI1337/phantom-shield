# NSS - Nexus Sovereign Standard v3.1.1

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![GDPR](https://img.shields.io/badge/GDPR-98%2F100-brightgreen.svg)](#compliance-ratings)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-96%2F100-brightgreen.svg)](#compliance-ratings)
[![Version](https://img.shields.io/badge/Version-3.1.1-blue.svg)](https://github.com/LEEI1337/NSS/releases)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![CI](https://img.shields.io/github/actions/workflow/status/LEEI1337/NSS/ci.yml?branch=main&label=CI)](https://github.com/LEEI1337/NSS/actions)

**Sovereign, GDPR-compliant AI infrastructure standard for the European Union.**

---

## Overview

NSS (Nexus Sovereign Standard) provides a **6-layer defensive architecture** with **Guardian Shield** for enterprise AI deployments. Built on **Mistral AI** models with local **Ollama** inference, NSS ensures zero Cloud Act exposure and full EU data sovereignty.

NSS is designed from the ground up to meet the strictest European regulatory requirements, including GDPR and the EU AI Act. Every component operates within EU borders, with no data leaving the sovereign perimeter. The architecture enforces privacy-by-design principles at every layer, from knowledge storage through cognitive processing to governance oversight.

---

## Key Features

- **Europa-First Architecture** -- Mistral AI foundation models with Ollama local inference; no US Cloud Act exposure
- **6-Layer Security** -- Guardian Shield with MARS, APEX, SENTINEL, SHIELD, and VIGIL subsystems
- **GDPR-Native Design** -- 98/100 compliance rating with built-in PII redaction, privacy budgets, and DPIA automation
- **EU AI Act Aligned** -- 96/100 compliance rating with full transparency, auditability, and risk classification
- **Cost Optimization** -- Up to 66% API cost savings via APEX intelligent model routing
- **Open Source + Commercial Support** -- Dual-licensed under AGPL-3.0 and Commercial License

---

## Architecture

```
+=====================================================================+
|                    Layer 5: Governance Plane                         |
|         Policy Engine  |  Privacy Budget  |  DPIA Automation        |
+=====================================================================+
|                    Layer 4: Guardian Shield                          |
|     MARS | APEX | SENTINEL | SHIELD | VIGIL                        |
|   (Model   (API    (Security   (System   (Validation                |
|   Audit)   Router)  Monitor)   Hardening) & Integrity)              |
+=====================================================================+
|                    Layer 3: Cognitive Gateway                        |
|         PII Redaction  |  STEER Routing  |  HMAC Signing            |
+=====================================================================+
|                    Layer 2: Agent Execution                          |
|         DPSparseVoteRAG  |  Tool Isolation  |  Sandboxing           |
+=====================================================================+
|                    Layer 1: Knowledge Fabric                         |
|         Qdrant Vector DB  |  Embeddings  |  Document Store          |
+=====================================================================+
```

Each layer enforces strict isolation boundaries. Requests flow upward from the Knowledge Fabric through Agent Execution, are filtered by the Cognitive Gateway, protected by Guardian Shield, and governed by the Governance Plane. No layer can be bypassed.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/LEEI1337/NSS.git
cd NSS

# Install NSS with development dependencies
pip install -e ".[dev]"

# Pull required Mistral models via Ollama
ollama pull mistral:7b-instruct-v0.3
ollama pull mistral-nemo:12b

# Start the Cognitive Gateway server
python -m nss.gateway.server
```

> **Prerequisites:** Python 3.11+, [Ollama](https://ollama.ai/) installed and running, Docker (optional, for Qdrant and Redis).

---

## Documentation

| Document | Description |
|----------|-------------|
| [White Paper](docs/white-paper/) | Full technical specification and design rationale |
| [Architecture](docs/architecture/) | Detailed architecture diagrams and component descriptions |
| [Security](docs/security/) | Security model, threat analysis, and Guardian Shield documentation |
| [Compliance](docs/compliance/) | GDPR, EU AI Act, and ISO 27001 compliance documentation |
| [Deployment](docs/deployment/) | Production deployment guides and infrastructure requirements |
| [Licensing](docs/licensing/) | License terms, commercial options, and contributor agreements |

---

## Compliance Ratings

| Standard | Rating | Status |
|----------|--------|--------|
| GDPR (General Data Protection Regulation) | **98/100** | Compliant |
| EU AI Act | **96/100** | Compliant |
| ISO 27001 | **4.1/5** | Aligned |
| STRIDE Threat Model | **9.7/10** | Secured |

All compliance ratings are based on independent assessment criteria documented in the [Compliance](docs/compliance/) section.

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|--------|
| LLM Provider | Mistral AI | Foundation models (Mistral 7B, Mistral-Nemo 12B) |
| Local Inference | Ollama | On-premises model serving with EU data residency |
| Vector Database | Qdrant | High-performance similarity search for RAG |
| Caching Layer | Redis | Session management and response caching |
| Policy Engine | OPA (Open Policy Agent) | Governance rules and access control |
| API Gateway | FastAPI | High-performance async HTTP gateway |
| Runtime | Python 3.11+ | Core application runtime |

---

## License

NSS is dual-licensed:

- **[AGPL-3.0](LICENSE)** -- For open-source use, research, and personal projects
- **[Commercial License](LICENSE-COMMERCIAL.md)** -- For proprietary deployments and enterprise use

If you use NSS in a proprietary product or service, you must obtain a commercial license. Contact [license@nss-standard.eu](mailto:license@nss-standard.eu) for details.

---

## Contributing

We welcome contributions from the community. Please read our [Contributing Guide](CONTRIBUTING.md) before submitting pull requests.

All contributors must agree to the [Contributor License Agreement (CLA)](CLA.md) to ensure license compatibility.

---

## Security

For security-related information, please see our [Security Policy](SECURITY.md).

- **Critical/High vulnerabilities:** Report via email to [security@nss-standard.eu](mailto:security@nss-standard.eu)
- **Low/Medium vulnerabilities:** Open a [Security Issue](https://github.com/LEEI1337/NSS/issues/new?template=security_vulnerability.yml)

---

## Author

**Jorg Fuchs** -- Technical Architect

- GitHub: [@LEEI1337](https://github.com/LEEI1337)
- Location: Austria

---

## Support

| Channel | Contact |
|---------|--------|
| Bug Reports | [GitHub Issues](https://github.com/LEEI1337/NSS/issues) |
| Discussions | [GitHub Discussions](https://github.com/LEEI1337/NSS/discussions) |
| General Support | [support@nss-standard.eu](mailto:support@nss-standard.eu) |
| Commercial Inquiries | [enterprise@nss-standard.eu](mailto:enterprise@nss-standard.eu) |

---

<p align="center">
  Made in Austria | Powered by Mistral AI | Secured by Guardian Shield
</p>
