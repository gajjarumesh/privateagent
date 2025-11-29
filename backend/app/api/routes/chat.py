"""Chat API endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_agent
from app.core.agent import Agent
from app.security import sanitize_input

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None
    module: str = Field(default="general", pattern="^(general|developer|trading|research)$")


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str
    session_id: str
    module: str
    tokens_used: Optional[int] = None


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(get_agent),
):
    """Process a chat message."""
    try:
        # Sanitize input
        sanitized_message = sanitize_input(request.message)
        if not sanitized_message:
            raise HTTPException(status_code=400, detail="Invalid message content")

        # Process through agent
        result = await agent.process(
            message=sanitized_message,
            session_id=request.session_id,
            module=request.module,
        )

        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            module=request.module,
            tokens_used=result.get("tokens_used"),
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(get_agent),
):
    """Get chat history for a session."""
    try:
        history = agent.memory.get_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    agent: Agent = Depends(get_agent),
):
    """Clear chat history for a session."""
    try:
        agent.memory.clear_session(session_id)
        return {"message": "History cleared", "session_id": session_id}
    except Exception as e:
        logger.error(f"Clear history error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear history")
