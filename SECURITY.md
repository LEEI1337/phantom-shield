# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 3.1.x   | Yes       |
| < 3.1   | No        |

## Reporting a Vulnerability

**DO NOT** open a public GitHub issue for security vulnerabilities.

### How to Report

Email: **security@nss-standard.eu**

Include:

- Description of the vulnerability
- Steps to reproduce
- Affected component (Gateway, Guardian Shield, Governance, Knowledge Fabric)
- Potential impact assessment
- Any suggested fixes

### Response Timeline

| Action | Timeline |
|--------|----------|
| Acknowledgment | Within 48 hours |
| Initial Assessment | Within 7 days |
| Fix for Critical | Within 30 days |
| Fix for High | Within 60 days |
| Fix for Medium/Low | Next release cycle |

### Scope

**In scope:**

- All NSS core components (Gateway, Guardian Shield, Governance Plane, Knowledge Fabric, Agent Execution)
- Docker and Kubernetes configurations
- CI/CD pipeline security
- Documentation that could lead to security issues

**Out of scope:**

- Third-party dependencies (report upstream)
- Social engineering attacks
- Denial of service attacks against test/demo instances

### Responsible Disclosure

We follow responsible disclosure practices. We ask that you:

- Allow reasonable time for fixes before public disclosure
- Do not access or modify other users' data
- Do not degrade the service

### Security Updates

Security advisories are published via [GitHub Security Advisories](https://github.com/LEEI1337/NSS/security/advisories).

### Hall of Fame

We thank the following individuals for responsibly disclosing vulnerabilities:

- *(This list will be updated as reports are received)*
