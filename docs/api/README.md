```
 █████╗ ██████╗ ██╗    ██████╗ ███████╗███████╗███████╗██████╗ ███████╗███╗   ██╗███████╗
██╔══██╗██╔══██╗██║    ██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗██╔════╝████╗  ██║╚══███╔╝
███████║██████╔╝██║    ██████╔╝█████╗  █████╗  █████╗  ██████╔╝█████╗  ██╔██╗ ██║  ███╔╝ 
██╔══██║██╔═══╝ ██║    ██╔══██╗██╔══╝  ██╔══╝  ██╔══╝  ██╔══██╗██╔══╝  ██║╚██╗██║ ███╔╝  
██║  ██║██║     ██║    ██║  ██║███████╗██║     ███████╗██║  ██║███████╗██║ ╚████║███████╗
╚═╝  ╚═╝╚═╝     ╚═╝    ╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚══════╝
```

# NSS v3.1 — API-Referenz

> **Nachrichtenformate, Protokolle und Schnittstellen für die Sovereign Neural Fabric**

---

## Inhaltsverzeichnis

- [Nachrichtentypen](#nachrichtentypen)
- [Gateway-API](#gateway-api)
- [Agent-API](#agent-api)
- [Knowledge-Fabric-API](#knowledge-fabric-api)
- [Governance-API](#governance-api)
- [Fehlerbehandlung](#fehlerbehandlung)

---

## Nachrichtentypen

### Übersicht

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          NSS v3.1 NACHRICHTENFLUSS                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│    CLIENT (C)           GATEWAY (G)           AGENT (A)           KNOWLEDGE (K)          │
│        │                     │                     │                     │               │
│        │                     │                     │                     │               │
│        │  IngressMessage     │                     │                     │               │
│        │────────────────────▶│                     │                     │               │
│        │                     │                     │                     │               │
│        │                     │  GatewayIntermed.   │                     │               │
│        │                     │────────────────────▶│                     │               │
│        │                     │                     │                     │               │
│        │                     │                     │  KnowledgeQuery     │               │
│        │                     │                     │────────────────────▶│               │
│        │                     │                     │                     │               │
│        │                     │                     │◀────────────────────│               │
│        │                     │                     │  KnowledgeResponse  │               │
│        │                     │                     │                     │               │
│        │                     │                     │  KnowledgeCommit    │               │
│        │                     │                     │────────────────────▶│               │
│        │                     │                     │                     │               │
│        │                     │◀────────────────────│                     │               │
│        │                     │  AgentResponse      │                     │               │
│        │                     │                     │                     │               │
│        │◀────────────────────│                     │                     │               │
│        │  EgressMessage      │                     │                     │               │
│        │                     │                     │                     │               │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### IngressMessage

**Richtung:** Client → Gateway

**Zweck:** Eingehende Anfrage vom Client an das Gateway

```json
{
  "$schema": "https://nss.standard/v3.1/schemas/ingress-message.json",
  "type": "IngressMessage",
  "version": "3.1",
  
  "ephemeral_id": {
    "type": "string",
    "format": "salted_nonce_hash_v2",
    "description": "Nicht-rückverfolgbare Session-Kennung",
    "example": "sha256(nonce + salt + timestamp)"
  },
  
  "session_nonce": {
    "type": "string",
    "format": "uuid-v4",
    "description": "Einmalige Session-Kennung",
    "example": "550e8400-e29b-41d4-a716-446655440000"
  },
  
  "timestamp": {
    "type": "string",
    "format": "ISO 8601",
    "description": "UTC-Zeitstempel der Anfrage",
    "example": "2026-02-06T10:36:00Z"
  },
  
  "payload_ciphertext": {
    "type": "string",
    "format": "base64",
    "description": "Verschlüsselter Payload (AES-256-GCM)",
    "example": "eyJhbGciOiJBMjU2R0NNIiwiZW5jIjoiQTI1NkdDTSJ9..."
  },
  
  "client_attestation": {
    "type": "string",
    "format": "base64",
    "description": "Hardware-Attestation des Clients (TPM Quote)",
    "example": "AQAB..."
  },
  
  "steer_params": {
    "type": "object",
    "description": "STEER-Transformationsparameter",
    "properties": {
      "transform_id": {
        "type": "string",
        "enum": ["steer_v3", "steer_v2", "none"],
        "description": "Angewandte STEER-Version"
      },
      "client_transformed": {
        "type": "boolean",
        "description": "Ob Client bereits STEER angewandt hat"
      }
    },
    "example": {"transform_id": "steer_v3", "client_transformed": false}
  },
  
  "privacy_tier_preference": {
    "type": "integer",
    "minimum": 0,
    "maximum": 3,
    "description": "Bevorzugter Privacy-Tier (0 = Maximum)",
    "example": 0
  }
}
```

**Beispiel:**

```json
{
  "ephemeral_id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "session_nonce": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-06T10:36:00Z",
  "payload_ciphertext": "eyJhbGciOiJBMjU2R0NNIiwiZW5jIjoiQTI1NkdDTSJ9.UGF5bG9hZA.dGVzdA",
  "client_attestation": "AQIDAAALBwAAAAABAAEAAQAAABQA...",
  "steer_params": {
    "transform_id": "steer_v3",
    "client_transformed": false
  },
  "privacy_tier_preference": 0
}
```

---

### GatewayIntermediate

**Richtung:** Gateway → Agent

**Zweck:** Bereinigte und transformierte Anfrage zur Agenten-Verarbeitung

```json
{
  "$schema": "https://nss.standard/v3.1/schemas/gateway-intermediate.json",
  "type": "GatewayIntermediate",
  "version": "3.1",
  
  "ephemeral_context": {
    "type": "string",
    "format": "encrypted",
    "description": "Bereinigter, PII-freier Kontext (TEE-verschlüsselt)",
    "example": "..."
  },
  
  "anonymized_features": {
    "type": "object",
    "description": "Anonymisierte Merkmale für Routing",
    "properties": {
      "topic_hash": {
        "type": "string",
        "description": "Hash des Themenbereichs"
      },
      "complexity_score": {
        "type": "number",
        "description": "Geschätzte Komplexität (0-1)"
      },
      "language": {
        "type": "string",
        "description": "Erkannte Sprache"
      }
    },
    "example": {"topic_hash": "sha256:abc123", "complexity_score": 0.7, "language": "de"}
  },
  
  "routing_token": {
    "type": "string",
    "format": "jwt",
    "description": "Signiertes Routing-Token",
    "example": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  
  "provenance_nonce": {
    "type": "string",
    "format": "uuid-v4",
    "description": "Nonce für Provenance-Tracking",
    "example": "660f8500-f30c-52e5-b827-557766551111"
  },
  
  "dp_budget_epsilon": {
    "type": "number",
    "minimum": 0,
    "description": "Zugewiesenes DP-Budget (ε)",
    "example": 1.5
  },
  
  "steer_transform_applied": {
    "type": "boolean",
    "description": "Ob STEER bereits angewendet wurde",
    "example": true
  },
  
  "privacy_tier": {
    "type": "integer",
    "minimum": 0,
    "maximum": 3,
    "description": "Zugewiesener Privacy-Tier",
    "example": 0
  },
  
  "pnc_metadata": {
    "type": "object",
    "description": "PNC v3.1 Kompressionsmetadaten",
    "properties": {
      "original_tokens": {"type": "integer"},
      "compressed_tokens": {"type": "integer"},
      "relevance_threshold": {"type": "number"}
    },
    "example": {"original_tokens": 2048, "compressed_tokens": 512, "relevance_threshold": 0.6}
  }
}
```

**Beispiel:**

```json
{
  "ephemeral_context": "encrypted_context_data_here",
  "anonymized_features": {
    "topic_hash": "sha256:7d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a",
    "complexity_score": 0.72,
    "language": "de"
  },
  "routing_token": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZ2VudCI6ImJhbGxpc3RpY3MifQ.sig",
  "provenance_nonce": "660f8500-f30c-52e5-b827-557766551111",
  "dp_budget_epsilon": 1.5,
  "steer_transform_applied": true,
  "privacy_tier": 0,
  "pnc_metadata": {
    "original_tokens": 2048,
    "compressed_tokens": 512,
    "relevance_threshold": 0.6
  }
}
```

---

### KnowledgeCommit

**Richtung:** Agent → Knowledge Fabric

**Zweck:** Persistierung neuer Erkenntnisse in der Wissensbasis

```json
{
  "$schema": "https://nss.standard/v3.1/schemas/knowledge-commit.json",
  "type": "KnowledgeCommit",
  "version": "3.1",
  
  "vector_id": {
    "type": "string",
    "format": "uuid-v4",
    "description": "Eindeutige Vektor-ID",
    "example": "770g9600-g41d-63f6-c938-668877662222"
  },
  
  "sag_encrypted_vector": {
    "type": "string",
    "format": "base64",
    "description": "SAG-verschlüsselter Vektor (AES-256-GCM)",
    "example": "..."
  },
  
  "steer_metadata": {
    "type": "object",
    "description": "STEER-Transformationsmetadaten",
    "properties": {
      "projection_matrix_hash": {
        "type": "string",
        "description": "Hash der verwendeten Projektionsmatrix"
      },
      "transform_version": {
        "type": "string",
        "description": "STEER-Version"
      },
      "source_dimension": {
        "type": "integer",
        "description": "Original-Dimension"
      },
      "target_dimension": {
        "type": "integer",
        "description": "Transformierte Dimension"
      }
    },
    "example": {
      "projection_matrix_hash": "sha256:abc123def456",
      "transform_version": "steer_v3",
      "source_dimension": 1536,
      "target_dimension": 768
    }
  },
  
  "provenance_tag": {
    "type": "object",
    "description": "Herkunftsinformationen (für Unlearning)",
    "properties": {
      "domain": {
        "type": "string",
        "description": "Wissensdomäne"
      },
      "age": {
        "type": "string",
        "format": "ISO 8601 duration",
        "description": "Alter der Information"
      },
      "unlearning_id": {
        "type": "string",
        "format": "uuid-v4",
        "description": "ID für Unlearning-Zuordnung"
      },
      "data_subject_hash": {
        "type": "string",
        "description": "Hash der betroffenen Person (falls zutreffend)"
      }
    },
    "example": {
      "domain": "ballistics",
      "age": "P1D",
      "unlearning_id": "880h0700-h52e-74g7-d049-779988773333",
      "data_subject_hash": null
    }
  },
  
  "dp_noise_level": {
    "type": "number",
    "minimum": 0,
    "maximum": 1,
    "description": "Angewandtes DP-Rauschniveau",
    "example": 0.8
  },
  
  "privacy_tier": {
    "type": "integer",
    "minimum": 0,
    "maximum": 3,
    "description": "Ziel-Privacy-Tier",
    "example": 2
  },
  
  "k_anonymity_pool": {
    "type": "integer",
    "minimum": 5,
    "description": "Minimale k-Anonymität-Pool-Größe",
    "example": 5
  }
}
```

**Beispiel:**

```json
{
  "vector_id": "770g9600-g41d-63f6-c938-668877662222",
  "sag_encrypted_vector": "QUVTLTI1Ni1HQ00gZW5jcnlwdGVkIHZlY3Rvcg==",
  "steer_metadata": {
    "projection_matrix_hash": "sha256:7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d",
    "transform_version": "steer_v3",
    "source_dimension": 1536,
    "target_dimension": 768
  },
  "provenance_tag": {
    "domain": "ballistics",
    "age": "P1D",
    "unlearning_id": "880h0700-h52e-74g7-d049-779988773333",
    "data_subject_hash": null
  },
  "dp_noise_level": 0.8,
  "privacy_tier": 2,
  "k_anonymity_pool": 5
}
```

---

### EgressMessage

**Richtung:** Gateway → Client

**Zweck:** Ausgehende Antwort vom Gateway an den Client

```json
{
  "$schema": "https://nss.standard/v3.1/schemas/egress-message.json",
  "type": "EgressMessage",
  "version": "3.1",
  
  "session_nonce": {
    "type": "string",
    "format": "uuid-v4",
    "description": "Korrespondierende Session-Nonce",
    "example": "550e8400-e29b-41d4-a716-446655440000"
  },
  
  "response_ciphertext": {
    "type": "string",
    "format": "base64",
    "description": "Verschlüsselte Antwort (AES-256-GCM)",
    "example": "..."
  },
  
  "privacy_attestation": {
    "type": "object",
    "description": "Nachweis der Privacy-Verarbeitung",
    "properties": {
      "tiers_used": {
        "type": "array",
        "items": {"type": "integer"},
        "description": "Verwendete Privacy-Tiers"
      },
      "dp_budget_consumed": {
        "type": "number",
        "description": "Verbrauchtes DP-Budget"
      },
      "pii_detected": {
        "type": "boolean",
        "description": "Ob PII erkannt und entfernt wurde"
      }
    },
    "example": {"tiers_used": [0, 2], "dp_budget_consumed": 0.3, "pii_detected": false}
  },
  
  "gateway_signature": {
    "type": "string",
    "format": "base64",
    "description": "ECDSA-Signatur des Gateways",
    "example": "MEUCIQDKZokN..."
  }
}
```

---

## Gateway-API

### Endpunkte

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          GATEWAY API (127.0.0.1:18789)                                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │  AUTHENTIFIZIERUNG                                                              │   │
│   │  ═════════════════                                                              │   │
│   │                                                                                 │   │
│   │  Alle Requests erfordern:                                                       │   │
│   │  • TLS 1.3 Client-Zertifikat                                                    │   │
│   │  • ClawdGuard Token im Header: Authorization: Bearer <token>                    │   │
│   │  • Optional: Client-Attestation im Body                                         │   │
│   │                                                                                 │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│   ENDPUNKTE:                                                                             │
│   ══════════                                                                             │
│                                                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                                 │   │
│   │  POST /v3.1/query                                                               │   │
│   │  ─────────────────                                                              │   │
│   │  Primärer Anfrage-Endpunkt                                                      │   │
│   │                                                                                 │   │
│   │  Request:  IngressMessage                                                       │   │
│   │  Response: EgressMessage                                                        │   │
│   │                                                                                 │   │
│   │  ─────────────────────────────────────────────────────────────────────────────  │   │
│   │                                                                                 │   │
│   │  GET /v3.1/health                                                               │   │
│   │  ────────────────────                                                           │   │
│   │  Gateway-Gesundheitscheck (nur von localhost)                                   │   │
│   │                                                                                 │   │
│   │  Response: {"status": "healthy", "version": "3.1", "tee_status": "active"}     │   │
│   │                                                                                 │   │
│   │  ─────────────────────────────────────────────────────────────────────────────  │   │
│   │                                                                                 │   │
│   │  POST /v3.1/attestation/verify                                                  │   │
│   │  ─────────────────────────────                                                  │   │
│   │  Client-Attestation-Verifizierung                                               │   │
│   │                                                                                 │   │
│   │  Request:  {"attestation": "base64...", "nonce": "uuid"}                        │   │
│   │  Response: {"valid": true, "expiry": "2026-02-06T11:36:00Z"}                    │   │
│   │                                                                                 │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Knowledge-Fabric-API

### Unlearning-API

```python
# Python SDK Beispiel

from nss_sdk import KnowledgeFabric, UnlearningRequest

kf = KnowledgeFabric(
    endpoint="https://knowledge.nss.local",
    credentials="credentials.json"
)

def request_unlearning(data_subject_id: str) -> UnlearningResult:
    """
    Anforderung zum Vergessen von Daten einer betroffenen Person
    gemäß DSGVO Art. 17
    
    Args:
        data_subject_id: Hash-ID der betroffenen Person
        
    Returns:
        UnlearningResult mit Audit-Trail
    """
    
    # 1. Identifiziere alle Vektoren mit Provenance-Tag
    vectors = kf.query_by_subject(
        subject_hash=data_subject_id,
        include_tiers=[1, 2]  # Tier 0 ist ephemeral, Tier 3 hat keine PII
    )
    
    # 2. Erzeuge Unlearning-Patch
    patch = kf.generate_negative_embedding(
        vectors=vectors,
        method="gradient_ascent",
        strength=0.8
    )
    
    # 3. Entferne/Anonymisiere Originalvektoren
    for v in vectors:
        if v.privacy_tier == 2:
            v.anonymize()  # Aggregation in Meta-Vektor
        else:
            v.delete()     # Vollständige Löschung
    
    # 4. Injiziere Patch
    kf.commit_patch(
        patch=patch,
        reason="GDPR_ART_17_REQUEST",
        subject_hash=data_subject_id
    )
    
    # 5. Audit-Log
    audit_entry = kf.governance.log_unlearning(
        data_subject_id=data_subject_id,
        vectors_affected=len(vectors),
        patch_hash=patch.hash,
        timestamp=datetime.utcnow()
    )
    
    return UnlearningResult(
        success=True,
        vectors_removed=len(vectors),
        audit_trail=audit_entry
    )
```

### Query-API

```python
# Sichere Knowledge-Abfrage mit Privacy-Garantien

def secure_query(
    query_embedding: List[float],
    dp_budget: float = 1.0,
    k: int = 5
) -> List[SecureResult]:
    """
    Führt eine privacy-preserving Ähnlichkeitssuche durch
    
    Args:
        query_embedding: STEER-transformierter Query-Vektor
        dp_budget: Maximal zu verbrauchendes DP-Budget (ε)
        k: Anzahl der zu retournierenden Ergebnisse
        
    Returns:
        Liste von SecureResult mit DP-Rauschen
    """
    
    # Prüfe ob Query bereits STEER-transformiert
    if not is_steer_transformed(query_embedding):
        raise SecurityError("Query must be STEER-transformed")
    
    # DPSparseVoteRAG-Suche
    results = kf.vector_search(
        query=query_embedding,
        top_k=k * 2,  # Overfetch für DP-Sampling
        tier_filter=[2]  # Nur Tier 2 (persistent, anonymisiert)
    )
    
    # Wende Differential Privacy an
    private_results = apply_dp_sampling(
        results=results,
        epsilon=dp_budget,
        k=k
    )
    
    return private_results
```

---

## Governance-API

### Policy-Engine

```yaml
# Beispiel: Privacy-Policy-Definition

policy:
  name: "high_security_tier0"
  version: "3.1.0"
  
  conditions:
    - type: "data_classification"
      value: "highly_sensitive"
    - type: "source_domain"
      value: ["medical", "financial", "legal"]
  
  actions:
    - action: "force_tier"
      tier: 0
      
    - action: "enforce_dp"
      epsilon_max: 0.5
      
    - action: "require_attestation"
      level: "hardware"
      
    - action: "log_audit"
      detail_level: "full"
      retention: "P10Y"  # 10 Jahre
  
  enforcement:
    mode: "strict"
    on_violation: "reject"
```

### Audit-Log-Format

```json
{
  "$schema": "https://nss.standard/v3.1/schemas/audit-log.json",
  "type": "AuditLogEntry",
  "version": "3.1",
  
  "entry_id": "990i1800-i63f-85h8-e150-880099884444",
  "timestamp": "2026-02-06T10:36:00.123Z",
  
  "event_type": "KNOWLEDGE_COMMIT",
  "event_category": "DATA_PROCESSING",
  
  "privacy_context": {
    "tier_used": 2,
    "dp_budget_consumed": 0.3,
    "k_anonymity_satisfied": true,
    "steer_applied": true,
    "sag_encrypted": true
  },
  
  "provenance": {
    "source_domain": "ballistics",
    "gateway_id": "gw-prod-01",
    "agent_id": "agent-ballistics-v2"
  },
  
  "integrity": {
    "hash_algorithm": "sha256",
    "entry_hash": "7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b",
    "previous_hash": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
    "signature": "MEUCIQD..."
  }
}
```

---

## Fehlerbehandlung

### Fehlercodes

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          NSS v3.1 FEHLERCODES                                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   CODE         BESCHREIBUNG                                 ABHILFE                      │
│   ═════════════════════════════════════════════════════════════════════════════════════ │
│                                                                                          │
│   GATEWAY ERRORS (1xxx)                                                                  │
│   ─────────────────────                                                                  │
│   1001         Loopback-Binding-Verletzung                  Nur 127.0.0.1 verwenden     │
│   1002         Attestation fehlgeschlagen                   Client-TPM prüfen           │
│   1003         Token abgelaufen                             Neues ClawdGuard-Token holen│
│   1004         TLS-Handshake fehlgeschlagen                 Zertifikate prüfen          │
│   1005         PII in Payload erkannt                       Payload bereinigen          │
│                                                                                          │
│   PRIVACY ERRORS (2xxx)                                                                  │
│   ────────────────────                                                                   │
│   2001         DP-Budget erschöpft                          Warten auf Reset            │
│   2002         k-Anonymität nicht erfüllbar                 Mehr Daten aggregieren      │
│   2003         STEER-Transformation fehlgeschlagen          Embedding-Format prüfen     │
│   2004         Privacy-Tier-Verletzung                      Niedrigeren Tier verwenden  │
│   2005         SAG-Verschlüsselung fehlgeschlagen           HSM-Verbindung prüfen       │
│                                                                                          │
│   KNOWLEDGE ERRORS (3xxx)                                                                │
│   ─────────────────────                                                                  │
│   3001         Vektor nicht gefunden                        Vector-ID prüfen            │
│   3002         Unlearning fehlgeschlagen                    Provenance-Tags prüfen      │
│   3003         Temporal-Aggregation-Fehler                  Zeit-Fenster prüfen         │
│   3004         Provenance-Konflikt                          Duplikat-Check durchführen  │
│                                                                                          │
│   AGENT ERRORS (4xxx)                                                                    │
│   ────────────────────                                                                   │
│   4001         Agent nicht verfügbar                        Agent-Status prüfen         │
│   4002         Skill-Execution-Fehler                       Skill-Logs prüfen           │
│   4003         DPSparseVoteRAG-Timeout                      Budget/Komplexität prüfen   │
│   4004         TEE-Isolation-Verletzung                     Sicherheitsaudit auslösen   │
│                                                                                          │
│   GOVERNANCE ERRORS (5xxx)                                                               │
│   ────────────────────────                                                               │
│   5001         Policy-Verletzung                            Policy anpassen/einhalten   │
│   5002         Audit-Log-Schreibfehler                      Governance-Plane prüfen     │
│   5003         Signatur-Verifizierung fehlgeschlagen        Zertifikatkette prüfen      │
│   5004         Compliance-Check fehlgeschlagen              DPIA-Dokumentation prüfen   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Fehler-Response-Format

```json
{
  "error": {
    "code": 2001,
    "message": "Differential Privacy budget exhausted for this session",
    "details": {
      "budget_allocated": 1.5,
      "budget_consumed": 1.5,
      "budget_remaining": 0.0,
      "reset_at": "2026-02-06T11:00:00Z"
    },
    "trace_id": "aa0j2900-j74g-96i9-f261-991100995555",
    "timestamp": "2026-02-06T10:45:00Z"
  }
}
```

---

<div align="center">

**NSS v3.1 API-Referenz** • **Stand: Februar 2026**

</div>
