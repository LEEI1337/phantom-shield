"""Tests for the async Ollama client."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from nss.llm.ollama_client import OllamaClient


class TestOllamaClient:
    """Unit tests for OllamaClient with mocked httpx responses."""

    async def test_generate(self) -> None:
        """generate() should POST to /api/generate and return the response text."""
        client = OllamaClient()

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Hello"}
        mock_response.raise_for_status = MagicMock()
        client._client.post = AsyncMock(return_value=mock_response)

        result = await client.generate(prompt="Say hello")

        assert result == "Hello"
        client._client.post.assert_awaited_once()
        call_args = client._client.post.call_args
        assert call_args[0][0] == "/api/generate"

    async def test_generate_with_confidence_tag(self) -> None:
        """generate_with_confidence() should extract [CONFIDENCE: X.X] tag."""
        client = OllamaClient()

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Answer [CONFIDENCE: 0.85]"}
        mock_response.raise_for_status = MagicMock()
        client._client.post = AsyncMock(return_value=mock_response)

        text, confidence = await client.generate_with_confidence(prompt="test")

        assert text == "Answer"
        assert confidence == pytest.approx(0.85)

    async def test_generate_with_confidence_no_tag(self) -> None:
        """generate_with_confidence() should default to 0.5 when no tag present."""
        client = OllamaClient()

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Answer without tag"}
        mock_response.raise_for_status = MagicMock()
        client._client.post = AsyncMock(return_value=mock_response)

        text, confidence = await client.generate_with_confidence(prompt="test")

        assert text == "Answer without tag"
        assert confidence == pytest.approx(0.5)

    async def test_health_check_success(self) -> None:
        """health_check() should return True on 200 response."""
        client = OllamaClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        client._client.get = AsyncMock(return_value=mock_response)

        result = await client.health_check()
        assert result is True

    async def test_health_check_failure(self) -> None:
        """health_check() should return False when an exception is raised."""
        import httpx

        client = OllamaClient()
        client._client.get = AsyncMock(side_effect=httpx.HTTPError("connection refused"))

        result = await client.health_check()
        assert result is False

    async def test_close(self) -> None:
        """close() should call aclose on the underlying client without errors."""
        client = OllamaClient()
        client._client.aclose = AsyncMock()

        await client.close()
        client._client.aclose.assert_awaited_once()
