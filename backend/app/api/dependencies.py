"""API dependencies."""

from typing import Generator
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import async_session
from app.core.agent import Agent
from app.core.llm_engine import LLMEngine
from app.core.memory import ConversationMemory


async def get_db() -> Generator[AsyncSession, None, None]:
    """Get database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


_llm_engine = None
_agent = None


def get_llm_engine() -> LLMEngine:
    """Get LLM engine instance."""
    global _llm_engine
    if _llm_engine is None:
        _llm_engine = LLMEngine()
    return _llm_engine


def get_agent() -> Agent:
    """Get agent instance."""
    global _agent
    if _agent is None:
        _agent = Agent(llm_engine=get_llm_engine())
    return _agent


def get_memory() -> ConversationMemory:
    """Get conversation memory instance."""
    return ConversationMemory()
