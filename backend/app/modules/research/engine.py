"""Research engine module for web search and document RAG."""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from app.core.llm_engine import LLMEngine

logger = logging.getLogger(__name__)

# DuckDuckGo for privacy-focused search
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logger.warning("duckduckgo-search not installed. Web search will be limited.")

# PyMuPDF for PDF processing
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF not installed. PDF processing will be limited.")


class ResearchEngine:
    """Research and document analysis engine."""

    def __init__(self, llm: Optional[LLMEngine] = None):
        """Initialize research engine."""
        self.llm = llm or LLMEngine()
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._chunks: List[Dict[str, Any]] = []

    async def process(
        self, message: str, context: str = ""
    ) -> Dict[str, Any]:
        """
        Process a research request.

        Args:
            message: User's request
            context: Conversation context

        Returns:
            Dict with response and metadata
        """
        system_prompt = """You are a research assistant specializing in information gathering and analysis.
You help users find information, analyze documents, and synthesize research.
Always cite your sources when providing information.
Be objective and present multiple perspectives when relevant.
If you're unsure about something, say so clearly."""

        prompt = f"""Previous context:
{context}

User: {message}

Provide a helpful research response that:
1. Addresses the user's question directly
2. Provides relevant information with context
3. Cites sources when applicable
4. Suggests follow-up research if relevant

Response:"""

        result = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
        )

        return result

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> Dict[str, Any]:
        """
        Perform web search using DuckDuckGo.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            Search results with optional summary
        """
        if not DDGS_AVAILABLE:
            return {
                "results": [],
                "error": "DuckDuckGo search is not available",
                "summary": None,
            }

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            formatted_results = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                }
                for r in results
            ]

            # Generate summary if results found
            summary = None
            if formatted_results:
                summary = await self._summarize_results(query, formatted_results)

            return {
                "results": formatted_results,
                "summary": summary,
            }

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {
                "results": [],
                "error": str(e),
                "summary": None,
            }

    async def _summarize_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
    ) -> str:
        """Summarize search results."""
        results_text = "\n\n".join([
            f"Title: {r['title']}\nSnippet: {r['snippet']}"
            for r in results
        ])

        prompt = f"""Based on the following search results for "{query}", provide a brief summary:

{results_text}

Provide a concise summary (2-3 sentences) of what the search results indicate about the query:"""

        result = await self.llm.generate(
            prompt=prompt,
            temperature=0.3,
        )

        return result.get("response", "")

    async def ingest_document(
        self,
        content: str,
        source: str = "user_input",
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Ingest a document for RAG.

        Args:
            content: Document content
            source: Source identifier
            metadata: Optional metadata

        Returns:
            Document ID
        """
        doc_id = str(uuid.uuid4())

        # Chunk the document
        chunks = self._chunk_text(content)

        # Store document
        self._documents[doc_id] = {
            "source": source,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunk_count": len(chunks),
        }

        # Store chunks with reference to document
        for i, chunk in enumerate(chunks):
            self._chunks.append({
                "doc_id": doc_id,
                "chunk_index": i,
                "content": chunk,
                "source": source,
            })

        logger.info(f"Ingested document {doc_id} with {len(chunks)} chunks")
        return doc_id

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)

        return chunks if chunks else [text]

    async def process_pdf(self, content: bytes) -> str:
        """
        Extract text from PDF content.

        Args:
            content: PDF file bytes

        Returns:
            Extracted text
        """
        if not PYMUPDF_AVAILABLE:
            raise ValueError("PDF processing is not available. Install PyMuPDF.")

        try:
            doc = fitz.open(stream=content, filetype="pdf")
            text_parts = []

            for page in doc:
                text_parts.append(page.get_text())

            doc.close()
            return "\n".join(text_parts)

        except Exception as e:
            logger.error(f"PDF processing error: {str(e)}")
            raise ValueError(f"Failed to process PDF: {str(e)}")

    async def query(
        self,
        question: str,
        session_id: Optional[str] = None,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        Query ingested documents using RAG.

        Args:
            question: User's question
            session_id: Optional session ID for context
            top_k: Number of relevant chunks to retrieve

        Returns:
            Answer with sources
        """
        # Simple keyword-based retrieval (production would use embeddings)
        relevant_chunks = self._retrieve_relevant(question, top_k)

        if not relevant_chunks:
            return {
                "answer": "I don't have any documents to search. Please upload or ingest documents first.",
                "sources": [],
            }

        # Build context from relevant chunks
        context = "\n\n".join([
            f"[Source: {c['source']}]\n{c['content']}"
            for c in relevant_chunks
        ])

        prompt = f"""Based on the following document excerpts, answer the question.
If the answer is not in the documents, say so clearly.

Documents:
{context}

Question: {question}

Answer (cite sources when possible):"""

        result = await self.llm.generate(
            prompt=prompt,
            temperature=0.3,
        )

        sources = list(set([c["source"] for c in relevant_chunks]))

        return {
            "answer": result.get("response", ""),
            "sources": sources,
        }

    def _retrieve_relevant(
        self,
        question: str,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks using simple keyword matching."""
        if not self._chunks:
            return []

        # Simple TF-based scoring
        question_words = set(question.lower().split())
        scored_chunks = []

        for chunk in self._chunks:
            chunk_words = set(chunk["content"].lower().split())
            score = len(question_words & chunk_words) / len(question_words) if question_words else 0
            scored_chunks.append((score, chunk))

        # Sort by score and return top_k
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored_chunks[:top_k] if _ > 0]

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all ingested documents."""
        return [
            {"id": doc_id, **info}
            for doc_id, info in self._documents.items()
        ]

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and its chunks."""
        if doc_id not in self._documents:
            return False

        del self._documents[doc_id]
        self._chunks = [c for c in self._chunks if c["doc_id"] != doc_id]

        logger.info(f"Deleted document {doc_id}")
        return True
