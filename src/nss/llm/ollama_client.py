"""Async Ollama client for local LLM inference.

Uses ``httpx`` to communicate with the Ollama HTTP API so that the
application stays fully async without blocking the event loop.
"""

from __future__ import annotations

import re

import httpx
import structlog

logger = structlog.get_logger(__name__)

_DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, privacy-aware AI assistant operating under the "
    "Nexus Sovereign Standard.  Always respect GDPR constraints."
)


class OllamaClient:
    """Thin async wrapper around the Ollama ``/api/generate`` endpoint.

    Parameters:
        base_url: Root URL of the Ollama server (e.g. ``http://localhost:11434``).
        default_model: Model tag used when no explicit model is passed to
            :meth:`generate`.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "mistral:7b-instruct-v0.3",
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    # -- public API ------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """Generate a completion from the Ollama API.

        Args:
            prompt: The user prompt to send to the model.
            model: Override the default model tag.
            system_prompt: Optional system prompt prepended to the conversation.

        Returns:
            The generated text response.
        """
        payload: dict[str, object] = {
            "model": model or self.default_model,
            "prompt": prompt,
            "system": system_prompt or _DEFAULT_SYSTEM_PROMPT,
            "stream": False,
        }
        response = await self._client.post("/api/generate", json=payload)
        response.raise_for_status()
        data: dict[str, object] = response.json()
        return str(data.get("response", ""))

    async def generate_with_confidence(
        self,
        prompt: str,
        model: str | None = None,
    ) -> tuple[str, float]:
        """Generate a response and extract a confidence score.

        The model is asked to append a ``[CONFIDENCE: <float>]`` tag.
        If the tag is missing the confidence defaults to ``0.5``.

        Args:
            prompt: The user prompt.
            model: Override the default model tag.

        Returns:
            A ``(response_text, confidence)`` tuple.
        """
        augmented_prompt = (
            f"{prompt}\n\nAfter your answer, append exactly one tag in the "
            "format [CONFIDENCE: <value>] where <value> is a float between 0 and 1."
        )
        raw = await self.generate(augmented_prompt, model=model)

        # Try to extract confidence tag
        confidence = 0.5
        match = re.search(r"\[CONFIDENCE:\s*([\d.]+)\]", raw)
        if match:
            try:
                confidence = min(max(float(match.group(1)), 0.0), 1.0)
            except ValueError:
                pass

        # Strip the confidence tag from the user-visible response
        clean = re.sub(r"\s*\[CONFIDENCE:\s*[\d.]+\]", "", raw).strip()
        return clean, confidence

    async def health_check(self) -> bool:
        """Return ``True`` if the Ollama server is reachable.

        Calls ``GET /api/tags`` which is a lightweight endpoint.
        """
        try:
            resp = await self._client.get("/api/tags")
            return resp.status_code == 200
        except httpx.HTTPError:
            logger.warning("ollama_health_check_failed")
            return False

    # -- lifecycle -------------------------------------------------------

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
