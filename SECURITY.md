```
███████╗███████╗ ██████╗██╗   ██╗██████╗ ██╗████████╗██╗   ██╗
██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝
███████╗█████╗  ██║     ██║   ██║██████╔╝██║   ██║    ╚████╔╝ 
╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██║   ██║     ╚██╔╝  
███████║███████╗╚██████╗╚██████╔╝██║  ██║██║   ██║      ██║   
╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝      ╚═╝   
```

# Sicherheitsrichtlinie — NSS v3.1

Dieses Dokument beschreibt die Sicherheitsrichtlinien für das Nexus Sovereign Standard (NSS v3.1) Projekt und wie Sicherheitsprobleme gemeldet werden können.

---

## 📋 Inhaltsverzeichnis

- [Unterstützte Versionen](#unterstützte-versionen)
- [Sicherheitslücken melden](#sicherheitslücken-melden)
- [Sicherheitsmaßnahmen](#sicherheitsmaßnahmen)
- [Bekannte Einschränkungen](#bekannte-einschränkungen)
- [Sicherheits-Updates](#sicherheits-updates)

---

## ✅ Unterstützte Versionen

| Version | Support-Status | Sicherheits-Updates |
|---------|---------------|---------------------|
| 3.1.x   | ✅ Aktiv       | Ja                  |
| 3.0.x   | ⚠️ Eingeschränkt | Nur kritische       |
| < 3.0   | ❌ Nicht unterstützt | Nein              |

---

## 🔒 Sicherheitslücken melden

### Privat melden (bevorzugt)

Für die Meldung von Sicherheitslücken nutzen Sie bitte **nicht** das öffentliche Issue-System.

**Kontaktieren Sie uns stattdessen über:**

1. **GitHub Security Advisories**: Nutzen Sie die "Report a vulnerability"-Funktion
2. **E-Mail**: Senden Sie Details an die im Profil hinterlegte Kontaktadresse

### Erforderliche Informationen

Bitte stellen Sie folgende Informationen bereit:

```
1. Zusammenfassung der Sicherheitslücke
2. Betroffene Komponente(n)
3. Schritte zur Reproduktion
4. Potenzielle Auswirkungen
5. Vorgeschlagene Lösung (falls vorhanden)
6. Ihre Kontaktinformationen
```

### Zeitrahmen

- **Bestätigung**: Innerhalb von 48 Stunden
- **Erste Bewertung**: Innerhalb von 7 Tagen
- **Fix-Entwicklung**: Je nach Schweregrad (siehe unten)
- **Disclosure**: Koordinierte Offenlegung nach Fix

### Schweregrade und Reaktionszeiten

| Schweregrad | Beschreibung | Reaktionszeit |
|-------------|--------------|---------------|
| **Kritisch** | Remote Code Execution, Datenexfiltration | 24-48 Stunden |
| **Hoch** | Authentifizierung umgehen, PII-Leak | 1 Woche |
| **Mittel** | Informationsoffenlegung, DoS | 2 Wochen |
| **Niedrig** | Theoretische Angriffe | Nächstes Release |

---

## 🛡️ Sicherheitsmaßnahmen

### NSS v3.1 Kernschutzmechanismen

Das NSS v3.1 Framework implementiert folgende Sicherheitsmaßnahmen:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SICHERHEITSSCHICHTEN                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  NETZWERK-EBENE                                             │     │
│  │  • Loopback-Binding (127.0.0.1:18789)                       │     │
│  │  • TLS 1.3 mit Mutual Authentication                        │     │
│  │  • Zertifikat-Pinning                                       │     │
│  │  • mDNS-Discovery-Blockierung                               │     │
│  └────────────────────────────────────────────────────────────┘     │
│                              │                                       │
│                              ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  AUTHENTIFIZIERUNG                                          │     │
│  │  • ClawdGuard Token-Validierung                             │     │
│  │  • Hardware-Attestation (TPM)                               │     │
│  │  • TEE-Remote-Attestation                                   │     │
│  └────────────────────────────────────────────────────────────┘     │
│                              │                                       │
│                              ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  DATEN-EBENE                                                │     │
│  │  • SAG Pre-Storage Full-Encryption (AES-256-GCM)            │     │
│  │  • STEER Nicht-invertierbare Transformation                 │     │
│  │  • k-Anonymität (k ≥ 5)                                     │     │
│  │  • Differential Privacy (DPSparseVoteRAG)                   │     │
│  └────────────────────────────────────────────────────────────┘     │
│                              │                                       │
│                              ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  VERARBEITUNG                                               │     │
│  │  • TEE-Isolation für sensitive Operationen                  │     │
│  │  • PII-Redaction im Gateway                                 │     │
│  │  • Privacy-Tier-Enforcement                                 │     │
│  │  • Machine Unlearning für Recht auf Vergessen               │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Schutz gegen bekannte Angriffsvektoren

| Angriffsvektor | NSS v3.1 Schutz | Status |
|----------------|-----------------|--------|
| Embedding-Inversion | STEER + SAG | ✅ Mitigiert |
| Netzwerk-Discovery | Loopback-Binding | ✅ Mitigiert |
| PII-Leakage | PII-Redaction + Tier 0 | ✅ Mitigiert |
| Privacy-Budget-Exhaustion | DPSparseVoteRAG | ✅ Mitigiert |
| Unerlaubte Datenpersistenz | Machine Unlearning | ✅ Mitigiert |
| Seitenkanalangriffe | TEE-Isolation | ⚠️ Teilweise mitigiert |

---

## ⚠️ Bekannte Einschränkungen

### Aktuelle Sicherheitshinweise

1. **TEE-Abhängigkeit**: Vollständiger Schutz erfordert Hardware-TEE (SGX/TrustZone)
2. **Seitenkanalattacken**: TEE-Isolation reduziert, eliminiert aber nicht alle Seitenkanalrisiken
3. **Key-Management**: HSM-Integration erforderlich für Produktionseinsatz

### Nicht im Scope

Folgende Punkte sind **nicht** Teil des Sicherheitsstandards:

- Client-seitige Sicherheit außerhalb der NSS-Spezifikation
- Physische Sicherheit der Hardware
- Social Engineering gegen Administratoren
- Zero-Day-Exploits in Drittanbieter-Software

---

## 📦 Sicherheits-Updates

### Benachrichtigung

Sicherheits-Updates werden angekündigt über:

- GitHub Security Advisories
- Release Notes
- CHANGELOG.md

### Update-Empfehlungen

1. **Kritische Updates**: Sofort einspielen
2. **Hohe Priorität**: Innerhalb von 7 Tagen
3. **Mittlere Priorität**: Nächstes Wartungsfenster
4. **Niedrige Priorität**: Nächstes geplantes Update

### Versionierung

Sicherheitsfixes folgen Semantic Versioning:

- **Patch** (x.x.X): Sicherheitsfix ohne Breaking Changes
- **Minor** (x.X.x): Neue Sicherheitsfeatures
- **Major** (X.x.x): Architekturelle Sicherheitsänderungen

---

## 🏆 Danksagungen

Wir danken allen, die verantwortungsvoll Sicherheitslücken melden. Ihre Unterstützung hilft, NSS sicher zu halten.

---

<div align="center">

**Sicherheit durch Design — NSS v3.1**

*„Stateless User, Stateful KI — das ist die Architektur des Vertrauens."*

</div>
