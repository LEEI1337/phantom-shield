# Contributing to NSS

Thank you for your interest in contributing to the Nexus Sovereign Standard.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

Use our [bug report template](https://github.com/LEEI1337/NSS/issues/new?template=bug_report.yml) on GitHub Issues.

### Suggesting Features

Use our [feature request template](https://github.com/LEEI1337/NSS/issues/new?template=feature_request.yml).

### Security Vulnerabilities

**Do not** open public issues for security vulnerabilities. See [SECURITY.md](SECURITY.md).

## Development Setup

```bash
# Clone the repository
git clone https://github.com/LEEI1337/NSS.git
cd NSS

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/

# Type check
mypy src/nss/
```

## Coding Standards

- **Python:** 3.11+ required
- **Linting:** ruff (PEP 8 compliant)
- **Type Checking:** mypy (strict mode)
- **Docstrings:** Google style
- **All functions** must have type hints

## Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Purpose |
|--------|---------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation |
| `security:` | Security improvement |
| `test:` | Tests |
| `refactor:` | Code refactoring |
| `ci:` | CI/CD changes |
| `chore:` | Maintenance |

## Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `security/description` - Security improvements

## Pull Request Process

1. Create a branch from `main`
2. Make your changes
3. Write/update tests
4. Run `ruff check` and `mypy`
5. Run `pytest`
6. Submit PR using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)
7. Wait for review

## Documentation

Documentation is bilingual (German/English) where applicable. Technical docs are in English, the White Paper is in German with English technical terms.
