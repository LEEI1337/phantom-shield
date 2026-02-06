```
 ██████╗ ██████╗ ███╗   ██╗████████╗██████╗ ██╗██████╗ ██╗   ██╗████████╗██╗███╗   ██╗ ██████╗ 
██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██║██╔══██╗██║   ██║╚══██╔══╝██║████╗  ██║██╔════╝ 
██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║██████╔╝██║   ██║   ██║   ██║██╔██╗ ██║██║  ███╗
██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║██╔══██╗██║   ██║   ██║   ██║██║╚██╗██║██║   ██║
╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║██║██████╔╝╚██████╔╝   ██║   ██║██║ ╚████║╚██████╔╝
 ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝    ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
```

# Beitragsrichtlinien für NSS v3.1

Vielen Dank für Ihr Interesse, zum Nexus Sovereign Standard beizutragen! Dieses Dokument enthält Richtlinien für Beiträge zum Projekt.

---

## 📋 Inhaltsverzeichnis

- [Verhaltenskodex](#verhaltenskodex)
- [Wie kann ich beitragen?](#wie-kann-ich-beitragen)
- [Entwicklungsworkflow](#entwicklungsworkflow)
- [Coding-Standards](#coding-standards)
- [Commit-Konventionen](#commit-konventionen)
- [Pull-Request-Prozess](#pull-request-prozess)

---

## 🤝 Verhaltenskodex

Dieses Projekt und alle Teilnehmer werden durch unseren Verhaltenskodex abgedeckt. Durch die Teilnahme erklären Sie sich mit der Einhaltung dieser Regeln einverstanden.

**Kernprinzipien:**
- Respektvoller und professioneller Umgang
- Konstruktive Kritik und offenes Feedback
- Fokus auf das Beste für die Gemeinschaft
- Inklusives und einladendes Umfeld

---

## 🚀 Wie kann ich beitragen?

### Fehler melden

Wenn Sie einen Fehler finden, erstellen Sie bitte ein Issue mit folgenden Informationen:

```
### Fehlerbeschreibung
[Klare und präzise Beschreibung des Fehlers]

### Schritte zur Reproduktion
1. [Erster Schritt]
2. [Zweiter Schritt]
3. [usw.]

### Erwartetes Verhalten
[Was Sie erwartet haben]

### Tatsächliches Verhalten
[Was tatsächlich passiert ist]

### Umgebung
- NSS-Version: 
- Betriebssystem: 
- Relevante Konfiguration:
```

### Verbesserungsvorschläge

Für neue Features oder Verbesserungen:

1. Prüfen Sie, ob bereits ein ähnliches Issue existiert
2. Erstellen Sie ein neues Issue mit dem Label `enhancement`
3. Beschreiben Sie den Anwendungsfall und den erwarteten Nutzen

### Dokumentation verbessern

Dokumentationsverbesserungen sind immer willkommen:

- Tippfehler korrigieren
- Erklärungen verbessern
- Beispiele hinzufügen
- Übersetzungen bereitstellen

---

## 🔧 Entwicklungsworkflow

### Repository klonen

```bash
git clone https://github.com/LEEI1337/NSS.git
cd NSS
```

### Branch erstellen

```bash
# Für Features
git checkout -b feature/meine-neue-funktion

# Für Bugfixes
git checkout -b fix/fehler-beschreibung

# Für Dokumentation
git checkout -b docs/dokumentations-update
```

### Änderungen vornehmen

1. Machen Sie Ihre Änderungen
2. Testen Sie Ihre Änderungen gründlich
3. Stellen Sie sicher, dass alle bestehenden Tests weiterhin funktionieren

### Pull Request erstellen

1. Pushen Sie Ihren Branch
2. Erstellen Sie einen Pull Request
3. Füllen Sie das PR-Template aus
4. Warten Sie auf Review

---

## 📝 Coding-Standards

### Allgemeine Prinzipien

- **Klarheit vor Cleverness**: Code sollte lesbar und verständlich sein
- **DRY (Don't Repeat Yourself)**: Vermeiden Sie Code-Duplikation
- **KISS (Keep It Simple, Stupid)**: Einfache Lösungen bevorzugen

### Dokumentation

Alle öffentlichen APIs und Funktionen müssen dokumentiert sein:

```python
def process_embedding(embedding: List[float], tier: int = 0) -> ProcessedEmbedding:
    """
    Verarbeitet ein Embedding gemäß NSS v3.1 Spezifikation.
    
    Args:
        embedding: Das zu verarbeitende Embedding als Liste von Floats
        tier: Der Privacy-Tier (0-3), Standard ist 0 (Maximum Privacy)
        
    Returns:
        ProcessedEmbedding mit STEER-Transformation und Metadaten
        
    Raises:
        ValueError: Wenn das Embedding-Format ungültig ist
        PrivacyError: Wenn der Tier nicht verfügbar ist
    """
    pass
```

### Security-First

Bei sicherheitsrelevanten Änderungen:

1. Führen Sie eine Sicherheitsanalyse durch
2. Dokumentieren Sie potenzielle Risiken
3. Implementieren Sie entsprechende Mitigationen
4. Lassen Sie den Code von einem zweiten Entwickler prüfen

---

## 💬 Commit-Konventionen

Wir verwenden [Conventional Commits](https://www.conventionalcommits.org/):

```
<typ>(<bereich>): <beschreibung>

[optionaler body]

[optionaler footer]
```

### Typen

| Typ | Beschreibung |
|-----|--------------|
| `feat` | Neue Funktion |
| `fix` | Fehlerbehebung |
| `docs` | Nur Dokumentation |
| `style` | Formatierung, kein Code-Change |
| `refactor` | Code-Änderung ohne Feature/Fix |
| `perf` | Performance-Verbesserung |
| `test` | Tests hinzufügen/korrigieren |
| `chore` | Build-Prozess, Hilfsmittel |
| `security` | Sicherheitsrelevante Änderung |

### Beispiele

```bash
feat(gateway): add STEER v3 transformation support

fix(knowledge-fabric): resolve k-anonymity calculation error

docs(api): update IngressMessage schema documentation

security(sag): upgrade to AES-256-GCM with HSM key management
```

---

## 🔍 Pull-Request-Prozess

### Checkliste

Vor dem Erstellen eines PR:

- [ ] Code folgt den Coding-Standards
- [ ] Dokumentation ist aktualisiert
- [ ] Tests sind hinzugefügt/aktualisiert
- [ ] Alle Tests bestehen
- [ ] Commit-Messages folgen der Konvention
- [ ] Branch ist auf dem neuesten Stand mit `main`

### Review-Prozess

1. **Automatische Checks**: CI/CD muss bestehen
2. **Code-Review**: Mindestens ein Maintainer muss approven
3. **Security-Review**: Bei sicherheitsrelevanten Änderungen
4. **Merge**: Nach Genehmigung durch Maintainer

### Merge-Strategie

- **Squash and Merge** für Feature-Branches
- **Rebase and Merge** für kleine Fixes
- **Merge Commit** nur für Release-Branches

---

## 📞 Kontakt

Bei Fragen wenden Sie sich an:

- **GitHub Issues**: Für technische Fragen und Bugs
- **GitHub Discussions**: Für allgemeine Diskussionen
- **Maintainer**: [@LEEI1337](https://github.com/LEEI1337)

---

<div align="center">

**Vielen Dank für Ihren Beitrag zum NSS v3.1 Standard!** 🙏

</div>
