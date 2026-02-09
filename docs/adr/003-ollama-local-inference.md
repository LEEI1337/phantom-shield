# ADR-003: Ollama for Local Model Inference

## Status

Accepted

## Context

NSS requires an inference runtime that runs foundation models entirely on-premises within EU borders. The runtime must be production-capable, easy to deploy, and support the chosen Mistral models.

## Decision

Use Ollama as the local inference runtime for all LLM operations.

## Rationale

- **Zero external API calls**: All inference happens on local hardware; no data leaves the EU perimeter
- **Simple deployment**: Single binary, Docker-native, pull-and-run model management
- **OpenAI-compatible API**: Standard REST API simplifies integration and future provider swaps
- **GPU support**: CUDA, ROCm, and Apple Silicon acceleration out of the box
- **Model management**: Built-in model pulling, versioning, and concurrent serving
- **Active ecosystem**: Large community, frequent updates, broad model support

## Alternatives Considered

- **vLLM**: Higher throughput but more complex deployment; overkill for reference implementation
- **llama.cpp**: Lower-level; requires manual model conversion and API wrapper
- **TGI (Text Generation Inference)**: Hugging Face solution; good but heavier deployment
- **Direct API calls**: Would violate data sovereignty requirements

## Consequences

- Ollama must be installed and running before NSS services start
- Model pull required on first deployment (`ollama pull mistral:7b-instruct-v0.3`)
- Performance depends on local GPU hardware
- Health check endpoint used for service readiness (`/api/tags`)
