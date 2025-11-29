"""Tests for the core agent module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.agent import Agent
from app.core.llm_engine import LLMEngine
from app.core.memory import ConversationMemory, Message


class TestConversationMemory:
    """Tests for ConversationMemory."""

    def test_create_session(self):
        """Test session creation."""
        memory = ConversationMemory()
        session_id = memory.create_session()

        assert session_id is not None
        assert len(session_id) > 0
        assert session_id in memory.list_sessions()

    def test_create_session_with_id(self):
        """Test session creation with custom ID."""
        memory = ConversationMemory()
        custom_id = "custom_session_123"
        session_id = memory.create_session(custom_id)

        assert session_id == custom_id

    def test_add_message(self):
        """Test adding messages to session."""
        memory = ConversationMemory()
        session_id = memory.create_session()

        message_id = memory.add_message(
            session_id=session_id,
            role="user",
            content="Hello, world!",
        )

        assert message_id is not None
        history = memory.get_history(session_id)
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello, world!"

    def test_max_history_limit(self):
        """Test that history is limited to max_history."""
        memory = ConversationMemory(max_history=3)
        session_id = memory.create_session()

        # Add 5 messages
        for i in range(5):
            memory.add_message(session_id, "user", f"Message {i}")

        history = memory.get_history(session_id)
        assert len(history) == 3
        # Should keep the most recent messages
        assert history[0]["content"] == "Message 2"
        assert history[2]["content"] == "Message 4"

    def test_get_context(self):
        """Test context generation."""
        memory = ConversationMemory()
        session_id = memory.create_session()

        memory.add_message(session_id, "user", "Hello")
        memory.add_message(session_id, "assistant", "Hi there!")

        context = memory.get_context(session_id)
        assert "USER: Hello" in context
        assert "ASSISTANT: Hi there!" in context

    def test_clear_session(self):
        """Test clearing session history."""
        memory = ConversationMemory()
        session_id = memory.create_session()

        memory.add_message(session_id, "user", "Hello")
        assert len(memory.get_history(session_id)) == 1

        result = memory.clear_session(session_id)
        assert result is True
        assert len(memory.get_history(session_id)) == 0

    def test_delete_session(self):
        """Test deleting a session."""
        memory = ConversationMemory()
        session_id = memory.create_session()

        memory.add_message(session_id, "user", "Hello")
        result = memory.delete_session(session_id)

        assert result is True
        assert session_id not in memory.list_sessions()


class TestMessage:
    """Tests for Message class."""

    def test_message_creation(self):
        """Test message creation."""
        msg = Message(role="user", content="Test message")

        assert msg.role == "user"
        assert msg.content == "Test message"
        assert msg.message_id is not None
        assert msg.timestamp is not None

    def test_message_to_dict(self):
        """Test message serialization."""
        msg = Message(role="assistant", content="Response")
        data = msg.to_dict()

        assert data["role"] == "assistant"
        assert data["content"] == "Response"
        assert "message_id" in data
        assert "timestamp" in data


class TestLLMEngine:
    """Tests for LLMEngine."""

    @pytest.mark.asyncio
    async def test_generate_timeout_handling(self):
        """Test that timeout errors are handled gracefully."""
        engine = LLMEngine()

        with patch("httpx.AsyncClient.post") as mock_post:
            import httpx
            mock_post.side_effect = httpx.TimeoutException("Timeout")

            result = await engine.generate("Test prompt")

            assert "error" in result
            assert result["error"] == "timeout"

    @pytest.mark.asyncio
    async def test_check_health_failure(self):
        """Test health check when Ollama is not available."""
        engine = LLMEngine()

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = Exception("Connection refused")

            is_healthy = await engine.check_health()

            assert is_healthy is False


class TestAgent:
    """Tests for Agent class."""

    @pytest.mark.asyncio
    async def test_process_creates_session(self):
        """Test that process creates a new session if none provided."""
        mock_llm = MagicMock(spec=LLMEngine)
        mock_llm.generate = AsyncMock(return_value={
            "response": "Hello!",
            "tokens_used": 10,
        })

        agent = Agent(llm_engine=mock_llm)
        result = await agent.process(message="Hi", module="general")

        assert "session_id" in result
        assert result["session_id"] is not None
        assert result["response"] == "Hello!"

    @pytest.mark.asyncio
    async def test_process_uses_existing_session(self):
        """Test that process uses existing session."""
        mock_llm = MagicMock(spec=LLMEngine)
        mock_llm.generate = AsyncMock(return_value={
            "response": "Response",
            "tokens_used": 5,
        })

        agent = Agent(llm_engine=mock_llm)

        # First message creates session
        result1 = await agent.process(message="First", module="general")
        session_id = result1["session_id"]

        # Second message uses same session
        result2 = await agent.process(
            message="Second",
            session_id=session_id,
            module="general",
        )

        assert result2["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_process_routes_to_developer(self):
        """Test that developer module is used."""
        mock_llm = MagicMock(spec=LLMEngine)
        mock_llm.generate = AsyncMock(return_value={
            "response": "Code help",
            "tokens_used": 20,
        })

        agent = Agent(llm_engine=mock_llm)
        result = await agent.process(
            message="Help with Python",
            module="developer",
        )

        assert result["module"] == "developer"

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test agent health check."""
        mock_llm = MagicMock(spec=LLMEngine)
        mock_llm.check_health = AsyncMock(return_value=True)

        agent = Agent(llm_engine=mock_llm)
        health = await agent.health_check()

        assert health["status"] == "healthy"
        assert health["llm"]["status"] == "healthy"
