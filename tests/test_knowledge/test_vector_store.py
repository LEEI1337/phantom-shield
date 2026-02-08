"""Tests for the Qdrant vector store wrapper."""

from unittest.mock import MagicMock, patch

import pytest

from nss.knowledge.vector_store import VectorStore


@pytest.fixture
def mock_qdrant_client() -> MagicMock:
    """A mocked QdrantClient."""
    client = MagicMock()
    # Simulate collection already exists
    mock_collection = MagicMock()
    mock_collection.name = "nss_documents"
    client.get_collections.return_value = MagicMock(collections=[mock_collection])
    return client


@pytest.fixture
def vector_store(mock_qdrant_client) -> VectorStore:
    """VectorStore with a mocked QdrantClient."""
    with patch("nss.knowledge.vector_store.QdrantClient", return_value=mock_qdrant_client):
        store = VectorStore()
    return store


class TestVectorStore:
    """Unit tests for VectorStore with mocked Qdrant."""

    async def test_search_returns_results(self, vector_store, mock_qdrant_client) -> None:
        """search() should return formatted results from Qdrant."""
        mock_result = MagicMock()
        mock_result.id = "doc-1"
        mock_result.score = 0.95
        mock_result.payload = {"text": "Sample document.", "user_id": "user-1"}
        mock_qdrant_client.search.return_value = [mock_result]

        results = await vector_store.search(query_embedding=[0.1] * 384, top_k=5)

        assert len(results) == 1
        assert results[0]["id"] == "doc-1"
        assert results[0]["score"] == 0.95
        assert results[0]["payload"]["text"] == "Sample document."

    async def test_search_empty(self, vector_store, mock_qdrant_client) -> None:
        """search() should return an empty list when no results are found."""
        mock_qdrant_client.search.return_value = []

        results = await vector_store.search(query_embedding=[0.1] * 384, top_k=5)
        assert results == []

    async def test_upsert(self, vector_store, mock_qdrant_client) -> None:
        """upsert() should call the Qdrant client's upsert method."""
        await vector_store.upsert(
            doc_id="doc-1",
            embedding=[0.1] * 384,
            payload={"text": "Test document.", "user_id": "user-1"},
        )
        mock_qdrant_client.upsert.assert_called_once()

    async def test_delete_by_user(self, vector_store, mock_qdrant_client) -> None:
        """delete_by_user() should call Qdrant delete and return 0."""
        result = await vector_store.delete_by_user(user_id="user-1")

        assert result == 0
        mock_qdrant_client.delete.assert_called_once()

    def test_collection_creation(self, mock_qdrant_client) -> None:
        """VectorStore should create a collection if it does not exist."""
        mock_qdrant_client.get_collections.return_value = MagicMock(collections=[])

        with patch("nss.knowledge.vector_store.QdrantClient", return_value=mock_qdrant_client):
            VectorStore(collection_name="new_collection")

        mock_qdrant_client.create_collection.assert_called_once()
