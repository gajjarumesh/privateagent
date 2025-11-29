"""Research API endpoints."""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from app.modules.research.engine import ResearchEngine
from app.security import sanitize_input

logger = logging.getLogger(__name__)
router = APIRouter()

# Create research engine instance
research_engine = ResearchEngine()


class SearchRequest(BaseModel):
    """Web search request model."""

    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=5, ge=1, le=20)


class SearchResponse(BaseModel):
    """Web search response model."""

    query: str
    results: List[dict]
    summary: Optional[str] = None


@router.post("/search", response_model=SearchResponse)
async def web_search(request: SearchRequest):
    """Perform a web search using DuckDuckGo."""
    try:
        sanitized_query = sanitize_input(request.query)
        if not sanitized_query:
            raise HTTPException(status_code=400, detail="Invalid search query")

        results = await research_engine.search(
            query=sanitized_query,
            max_results=request.max_results,
        )

        return SearchResponse(
            query=sanitized_query,
            results=results["results"],
            summary=results.get("summary"),
        )
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")


class DocumentRequest(BaseModel):
    """Document ingestion request model."""

    content: str = Field(..., min_length=1, max_length=100000)
    source: str = Field(default="user_input")
    metadata: Optional[dict] = None


@router.post("/ingest")
async def ingest_document(request: DocumentRequest):
    """Ingest a document for RAG."""
    try:
        sanitized_content = sanitize_input(request.content)
        if not sanitized_content:
            raise HTTPException(status_code=400, detail="Invalid document content")

        doc_id = await research_engine.ingest_document(
            content=sanitized_content,
            source=request.source,
            metadata=request.metadata,
        )

        return {
            "message": "Document ingested successfully",
            "document_id": doc_id,
        }
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to ingest document")


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file (PDF or text)."""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "text/plain", "text/markdown"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not supported",
            )

        # Read file content
        content = await file.read()

        # Process based on type
        if file.content_type == "application/pdf":
            text = await research_engine.process_pdf(content)
        else:
            text = content.decode("utf-8")

        # Ingest the document
        doc_id = await research_engine.ingest_document(
            content=text,
            source=file.filename or "uploaded_file",
            metadata={"content_type": file.content_type},
        )

        return {
            "message": "File processed and ingested",
            "filename": file.filename,
            "document_id": doc_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process file")


class QueryRequest(BaseModel):
    """RAG query request model."""

    question: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None


@router.post("/query")
async def query_documents(request: QueryRequest):
    """Query ingested documents using RAG."""
    try:
        sanitized_question = sanitize_input(request.question)
        if not sanitized_question:
            raise HTTPException(status_code=400, detail="Invalid question")

        result = await research_engine.query(
            question=sanitized_question,
            session_id=request.session_id,
        )

        return {
            "question": sanitized_question,
            "answer": result["answer"],
            "sources": result.get("sources", []),
        }
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail="Query failed")
