"""RAG (Retrieval Augmented Generation) utilities."""

import logging
from typing import List, Dict, Any, Optional
import hashlib

logger = logging.getLogger(__name__)


class RAGStore:
    """Simple in-memory RAG storage for document chunks."""

    def __init__(self):
        """Initialize RAG store."""
        self._chunks: Dict[str, Dict[str, Any]] = {}
        self._index: Dict[str, List[str]] = {}  # word -> chunk_ids

    def add_chunk(
        self,
        content: str,
        doc_id: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """Add a chunk to the store."""
        chunk_id = hashlib.md5(content.encode()).hexdigest()[:16]

        self._chunks[chunk_id] = {
            "content": content,
            "doc_id": doc_id,
            "metadata": metadata or {},
        }

        # Index words for retrieval
        words = set(content.lower().split())
        for word in words:
            if word not in self._index:
                self._index[word] = []
            if chunk_id not in self._index[word]:
                self._index[word].append(chunk_id)

        return chunk_id

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search for relevant chunks."""
        query_words = set(query.lower().split())

        # Score chunks by word overlap
        chunk_scores: Dict[str, float] = {}

        for word in query_words:
            if word in self._index:
                for chunk_id in self._index[word]:
                    chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1

        # Normalize scores
        if query_words:
            for chunk_id in chunk_scores:
                chunk_scores[chunk_id] /= len(query_words)

        # Sort and return top_k
        sorted_chunks = sorted(
            chunk_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

        return [
            {
                "chunk_id": chunk_id,
                "score": score,
                **self._chunks[chunk_id],
            }
            for chunk_id, score in sorted_chunks
        ]

    def delete_by_doc(self, doc_id: str) -> int:
        """Delete all chunks for a document."""
        to_delete = [
            chunk_id for chunk_id, chunk in self._chunks.items()
            if chunk["doc_id"] == doc_id
        ]

        for chunk_id in to_delete:
            chunk = self._chunks.pop(chunk_id)
            words = set(chunk["content"].lower().split())
            for word in words:
                if word in self._index and chunk_id in self._index[word]:
                    self._index[word].remove(chunk_id)

        return len(to_delete)

    def clear(self) -> None:
        """Clear all stored data."""
        self._chunks.clear()
        self._index.clear()

    @property
    def chunk_count(self) -> int:
        """Get total number of chunks."""
        return len(self._chunks)
