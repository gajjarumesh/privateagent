"""Feedback API endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.core.learning import FeedbackLearning
from app.database.models import Feedback
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = APIRouter()

# Create feedback learning instance
feedback_learning = FeedbackLearning()


class FeedbackRequest(BaseModel):
    """Feedback submission request model."""

    session_id: str = Field(..., min_length=1, max_length=100)
    message_id: str = Field(..., min_length=1, max_length=100)
    rating: int = Field(..., ge=-1, le=1, description="-1=thumbs down, 0=neutral, 1=thumbs up")
    correction: Optional[str] = Field(None, max_length=10000)
    module: str = Field(default="general")


class FeedbackResponse(BaseModel):
    """Feedback submission response model."""

    message: str
    feedback_id: str


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback for a response."""
    try:
        feedback_id = await feedback_learning.store_feedback(
            db=db,
            session_id=request.session_id,
            message_id=request.message_id,
            rating=request.rating,
            correction=request.correction,
            module=request.module,
        )

        return FeedbackResponse(
            message="Feedback recorded successfully",
            feedback_id=feedback_id,
        )
    except Exception as e:
        logger.error(f"Feedback submission error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.get("/stats")
async def get_feedback_stats(
    db: AsyncSession = Depends(get_db),
    module: Optional[str] = None,
):
    """Get feedback statistics."""
    try:
        stats = await feedback_learning.get_stats(db, module=module)
        return stats
    except Exception as e:
        logger.error(f"Stats retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")


@router.get("/history/{session_id}")
async def get_feedback_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get feedback history for a session."""
    try:
        stmt = select(Feedback).where(Feedback.session_id == session_id)
        result = await db.execute(stmt)
        feedbacks = result.scalars().all()

        return {
            "session_id": session_id,
            "feedbacks": [
                {
                    "id": str(f.id),
                    "message_id": f.message_id,
                    "rating": f.rating,
                    "correction": f.correction,
                    "module": f.module,
                    "created_at": f.created_at.isoformat(),
                }
                for f in feedbacks
            ],
        }
    except Exception as e:
        logger.error(f"Feedback history error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve feedback history")
