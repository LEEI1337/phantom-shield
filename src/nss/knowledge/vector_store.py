"""Qdrant vector-store wrapper for RAG and GDPR Article 17 compliance.

Provides async search, upsert, and user-level deletion (right to be
forgotten) operations.
"""

from __future__ import annotations

from typing import Any

import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

logger = structlog.get_logger(__name__)


class VectorStore:
    """Thin wrapper around a Qdrant collection.

    Parameters:
        host: Qdrant server hostname.
        port: Qdrant gRPC port.
        collection_name: Name of the target collection (created on first
            use if it does not exist).
        vector_size: Dimensionality of stored embeddings (default ``384``
            for ``all-MiniLM-L6-v2``).
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "nss_documents",
        vector_size: int = 384,
    ) -> None:
        self.collection_name = collection_name
        self._vector_size = vector_size
        self._client = QdrantClient(host=host, port=port)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create the collection if it does not already exist."""
        collections = [c.name for c in self._client.get_collections().collections]
        if self.collection_name not in collections:
            self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self._vector_size,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("collection_created", name=self.collection_name)

    # -- Public API ------------------------------------------------------

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search the collection for the nearest neighbours.

        Args:
            query_embedding: Query vector (must match ``vector_size``).
            top_k: Number of results to return.

        Returns:
            List of dicts with ``id``, ``score``, and ``payload`` keys.
        """
        results = self._client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
        )
        return [
            {
                "id": str(r.id),
                "score": r.score,
                "payload": r.payload or {},
            }
            for r in results
        ]

    async def upsert(
        self,
        doc_id: str,
        embedding: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Insert or update a single document.

        Args:
            doc_id: Unique document identifier.
            embedding: Document embedding vector.
            payload: Arbitrary metadata stored alongside the vector.
        """
        self._client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload=payload,
                ),
            ],
        )

    async def delete_by_user(self, user_id: str) -> int:
        """Delete all documents belonging to *user_id* (GDPR Art. 17).

        Args:
            user_id: The user whose data must be erased.

        Returns:
            Number of points deleted (approximate -- Qdrant may report 0
            even on success in some versions).
        """
        self._client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id),
                    ),
                ],
            ),
        )
        logger.info("user_data_deleted", user_id=user_id)
        # Qdrant does not return a count on delete; return 0 as sentinel.
        return 0
