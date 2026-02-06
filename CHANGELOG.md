```
 ██████╗██╗  ██╗ █████╗ ███╗   ██╗ ██████╗ ███████╗██╗      ██████╗  ██████╗ 
██╔════╝██║  ██║██╔══██╗████╗  ██║██╔════╝ ██╔════╝██║     ██╔═══██╗██╔════╝ 
██║     ███████║███████║██╔██╗ ██║██║  ███╗█████╗  ██║     ██║   ██║██║  ███╗
██║     ██╔══██║██╔══██║██║╚██╗██║██║   ██║██╔══╝  ██║     ██║   ██║██║   ██║
╚██████╗██║  ██║██║  ██║██║ ╚████║╚██████╔╝███████╗███████╗╚██████╔╝╚██████╔╝
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝ ╚═════╝  ╚═════╝ 
```

# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

---

## [3.1.0] — 2026-02-06

### 🚀 Hinzugefügt

#### Sicherheit
- **Pre-Storage Full-Encryption (SAG)**: Vollständige Verschlüsselung aller Daten vor Speicherung
  - AES-256-GCM Verschlüsselung im TEE
  - Envelope-Encryption mit HSM-geschützten Root-Keys
  - Attribute-Based Encryption für Domänen-selektiven Zugriff

- **STEER (Secure Transformed Embedding vEctor Retrieval)**: Schutz vor Embedding-Inversion
  - Nicht-invertierbare Vektortransformation
  - < 5% Retrieval-Qualitätsverlust
  - > 95% Reduktion der Inversion-Genauigkeit

- **Netzwerk-Härtung**:
  - Loopback-Binding (127.0.0.1:18789)
  - mDNS/Avahi-Deaktivierung
  - ClawdGuard-Integration für Token-Management

#### Privacy
- **DPSparseVoteRAG**: Optimierte Differential-Privacy-Budget-Nutzung
  - Token-selektive Rausch-Injektion
  - 3-5x bessere Budget-Effizienz gegenüber naivem DP-RAG
  - Vergleichbare Qualität bei ε ≈ 10

- **Privacy-Tier-Architektur**:
  - Tier 0: Ephemeral Context (< 5 min, keine Persistenz)
  - Tier 1: Transient Embeddings (Session-gebunden)
  - Tier 2: Persistent Knowledge (SAG-verschlüsselt, k-anonym)
  - Tier 3: Governance Metadata (Audit-only)

- **Machine Unlearning**: Technische Umsetzung des Rechts auf Vergessen
  - Provenance-Tracking für alle Vektoren
  - Negative-Embedding-Patch-Injektion
  - Audit-Trail für Unlearning-Operationen

#### Gateway
- **PNC v3.1 Kompression**: Adaptives Kontext-Window-Pruning
  - Relevanz-Scoring: r(t) = α·saliency(t) + β·recency(t) - γ·redundancy(t)
  
- **Erweiterte Pipeline** (9 Stufen):
  1. Loopback-Binding-Check
  2. Authentifikation & Attestation
  3. TEE-Entschlüsselung
  4. PII-Redaction mit Proof
  5. STEER-Transformation
  6. Privacy-Tier-Enforcement
  7. PNC v3.1 Kompression
  8. DPSparseVoteRAG-Routing
  9. SAG-Verschlüsselung

#### Compliance
- **EU-AI-Verordnung-Mapping**: Art. 9, 10, 13, 15
- **DSGVO-Mapping**: Art. 5, 17, 25, 32, 35
- **DPIA-Vorlage**: Standardisierte Datenschutz-Folgenabschätzung

#### Dokumentation
- Enterprise-README mit ASCII-Art
- Umfassende Architektur-Dokumentation
- Sicherheitsarchitektur-Dokumentation
- API-Referenz mit Nachrichtenformaten
- Compliance-Dokumentation

### 🔧 Geändert

- Gateway-Port von dynamisch zu fix: **18789**
- Verschlüsselung: AES-128 → **AES-256-GCM**
- k-Anonymität-Minimum: k=3 → **k=5**
- Privacy-Budget-Tracking: Global → **Per-Session**

### 🔒 Sicherheit

- Schutz gegen Embedding-Inversion-Angriffe (> 70% Rekonstruktionsgenauigkeit eliminiert)
- Schutz gegen mDNS-Leaks und Gateway-Topologie-Offenlegung
- Schutz gegen Privacy-Budget-Erschöpfung
- Verbesserter TEE-Isolation-Mechanismus

### 📚 Referenzen

Neue wissenschaftliche Grundlagen integriert:
- [arXiv:2412.04697] Privacy-Preserving RAG with DP
- [arXiv:2507.18518] Transform Before You Query (STEER)
- [AlphaXiv:2504.00147v1] Universal Zero-shot Embedding Inversion
- [arXiv:2406.00966] Federated Unlearning with DP
- [arXiv:2311.15603] QuickDrop Federated Unlearning
- [arXiv:2501.18636] SafeRAG Security Benchmarking

---

## [3.0.0] — 2025-09-15

### 🚀 Hinzugefügt

- Initiale Sovereign Neural Fabric (SNF) Architektur
- 5-Domänen-Modell (C, G, A, K, M)
- Grundlegende Privacy-Mechanismen
- k-Anonymität (k=3)
- Basis-Differential-Privacy

### 📝 Hinweise

Diese Version diente als Grundlage für v3.1 und wird nicht mehr aktiv weiterentwickelt.
Sicherheitsupdates werden nur für kritische Lücken bereitgestellt.

---

## Legende

- 🚀 Hinzugefügt: Neue Funktionen
- 🔧 Geändert: Änderungen an bestehenden Funktionen
- ⚠️ Veraltet: Bald zu entfernende Funktionen
- 🗑️ Entfernt: Entfernte Funktionen
- 🐛 Behoben: Fehlerbehebungen
- 🔒 Sicherheit: Sicherheitsrelevante Änderungen

---

<div align="center">

**NSS Changelog** • Dokumentenstand: Februar 2026

</div>
