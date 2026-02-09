# ADR-002: Mistral AI as Foundation Model Provider

## Status

Accepted

## Context

NSS requires foundation language models for risk scoring (MARS), injection detection (SENTINEL), and user query processing. The model provider must support EU data sovereignty requirements.

## Decision

Use Mistral AI models (Mistral 7B Instruct, Mistral-Nemo 12B) as foundation models.

## Rationale

- **EU-headquartered**: Mistral AI is a French company; no US Cloud Act / FISA Section 702 exposure
- **Open-weight models**: Weights are downloadable and can run fully on-premises
- **Performance/cost ratio**: Mistral 7B provides strong performance at minimal compute cost; Mistral-Nemo 12B handles complex queries
- **APEX routing**: Two model tiers enable intelligent cost optimization (66% API cost savings via routing)
- **Apache 2.0 license**: Mistral models can be used commercially without restrictions

## Alternatives Considered

- **OpenAI GPT-4**: Superior performance but US-based; Cloud Act exposure; no local inference
- **Anthropic Claude**: US-based; no open-weight models available for local deployment
- **LLaMA 3 (Meta)**: US-based company; license restricts some commercial uses
- **Aleph Alpha (Luminous)**: German company but limited model availability and ecosystem

## Consequences

- Models must be pulled and served via Ollama before deployment
- GPU infrastructure required for local inference (minimum 8GB VRAM for 7B, 16GB for 12B)
- Model quality depends on Mistral AI's continued development
