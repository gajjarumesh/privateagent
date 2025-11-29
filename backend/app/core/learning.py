"""Feedback learning system for improving responses."""

import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.models import Feedback, LearningPattern

logger = logging.getLogger(__name__)


class FeedbackLearning:
    """Manages feedback collection and learning patterns."""

    def __init__(self):
        """Initialize feedback learning system."""
        self._patterns: Dict[str, Dict[str, Any]] = {}

    async def store_feedback(
        self,
        db: AsyncSession,
        session_id: str,
        message_id: str,
        rating: int,
        correction: Optional[str] = None,
        module: str = "general",
    ) -> str:
        """
        Store user feedback in the database.

        Args:
            db: Database session
            session_id: Conversation session ID
            message_id: ID of the message being rated
            rating: -1 (thumbs down), 0 (neutral), 1 (thumbs up)
            correction: Optional user-provided correction
            module: The module that generated the response

        Returns:
            Feedback ID
        """
        feedback_id = str(uuid.uuid4())

        feedback = Feedback(
            id=uuid.UUID(feedback_id),
            session_id=session_id,
            message_id=message_id,
            rating=rating,
            correction=correction,
            module=module,
            created_at=datetime.now(timezone.utc),
        )

        db.add(feedback)
        await db.commit()

        logger.info(f"Stored feedback: {feedback_id} (rating: {rating})")

        # Process learning if correction provided
        if correction and rating < 0:
            await self._process_correction(db, feedback)

        return feedback_id

    async def _process_correction(
        self,
        db: AsyncSession,
        feedback: Feedback,
    ) -> None:
        """Process a correction to learn from it."""
        try:
            # Create a learning pattern from the correction
            pattern = LearningPattern(
                id=uuid.uuid4(),
                module=feedback.module,
                pattern_type="correction",
                pattern_data={
                    "message_id": feedback.message_id,
                    "correction": feedback.correction,
                    "session_id": feedback.session_id,
                },
                weight=1.0,
                created_at=datetime.now(timezone.utc),
            )

            db.add(pattern)
            await db.commit()

            logger.info(f"Created learning pattern from feedback: {feedback.id}")

        except Exception as e:
            logger.error(f"Failed to process correction: {str(e)}")

    async def get_stats(
        self,
        db: AsyncSession,
        module: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get feedback statistics."""
        try:
            # Base query
            query = select(
                func.count(Feedback.id).label("total"),
                func.sum(func.case((Feedback.rating > 0, 1), else_=0)).label("positive"),
                func.sum(func.case((Feedback.rating < 0, 1), else_=0)).label("negative"),
                func.sum(func.case((Feedback.rating == 0, 1), else_=0)).label("neutral"),
                func.count(Feedback.correction).label("corrections"),
            )

            if module:
                query = query.where(Feedback.module == module)

            result = await db.execute(query)
            row = result.first()

            if row:
                total = row.total or 0
                positive = row.positive or 0
                negative = row.negative or 0

                return {
                    "total_feedback": total,
                    "positive": positive,
                    "negative": negative,
                    "neutral": row.neutral or 0,
                    "corrections": row.corrections or 0,
                    "satisfaction_rate": (positive / total * 100) if total > 0 else 0,
                    "module": module or "all",
                }

            return {
                "total_feedback": 0,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "corrections": 0,
                "satisfaction_rate": 0,
                "module": module or "all",
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {"error": str(e)}

    async def get_patterns(
        self,
        db: AsyncSession,
        module: str,
        limit: int = 10,
    ) -> list:
        """Get learning patterns for a module."""
        try:
            query = (
                select(LearningPattern)
                .where(LearningPattern.module == module)
                .order_by(LearningPattern.weight.desc())
                .limit(limit)
            )

            result = await db.execute(query)
            patterns = result.scalars().all()

            return [
                {
                    "id": str(p.id),
                    "type": p.pattern_type,
                    "data": p.pattern_data,
                    "weight": p.weight,
                }
                for p in patterns
            ]

        except Exception as e:
            logger.error(f"Failed to get patterns: {str(e)}")
            return []

    def apply_learning(self, response: str, module: str) -> str:
        """Apply learned patterns to improve a response."""
        # This is a placeholder for more sophisticated learning
        # In a production system, this would use the stored patterns
        # to modify or improve responses
        return response
