"""Conversation memory management."""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

from app.config import settings
from app.security import generate_session_id

logger = logging.getLogger(__name__)


class Message:
    """Represents a single message in conversation."""

    def __init__(
        self,
        role: str,
        content: str,
        message_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        self.role = role
        self.content = content
        self.message_id = message_id or generate_session_id()[:16]
        self.timestamp = datetime.utcnow()
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class ConversationMemory:
    """Manages conversation history and context."""

    def __init__(self, max_history: Optional[int] = None):
        """Initialize conversation memory."""
        self.max_history = max_history or settings.max_conversation_history
        self._sessions: Dict[str, List[Message]] = defaultdict(list)
        self._metadata: Dict[str, dict] = {}

    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new conversation session."""
        session_id = session_id or generate_session_id()
        self._sessions[session_id] = []
        self._metadata[session_id] = {
            "created_at": datetime.utcnow().isoformat(),
            "message_count": 0,
        }
        logger.info(f"Created new session: {session_id}")
        return session_id

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """Add a message to a session."""
        if session_id not in self._sessions:
            self.create_session(session_id)

        message = Message(role=role, content=content, metadata=metadata)
        self._sessions[session_id].append(message)

        # Trim history if needed
        if len(self._sessions[session_id]) > self.max_history:
            self._sessions[session_id] = self._sessions[session_id][-self.max_history:]

        # Update metadata
        if session_id in self._metadata:
            self._metadata[session_id]["message_count"] = len(self._sessions[session_id])
            self._metadata[session_id]["last_message_at"] = datetime.utcnow().isoformat()

        return message.message_id

    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[dict]:
        """Get conversation history for a session."""
        if session_id not in self._sessions:
            return []

        messages = self._sessions[session_id]
        if limit:
            messages = messages[-limit:]

        return [msg.to_dict() for msg in messages]

    def get_context(self, session_id: str, max_tokens: Optional[int] = None) -> str:
        """Get formatted context string for LLM prompt."""
        max_tokens = max_tokens or settings.max_context_tokens
        history = self.get_history(session_id)

        context_parts = []
        estimated_tokens = 0

        # Build context from most recent messages
        for msg in reversed(history):
            msg_text = f"{msg['role'].upper()}: {msg['content']}"
            msg_tokens = len(msg_text.split()) * 1.3  # Rough token estimate

            if estimated_tokens + msg_tokens > max_tokens:
                break

            context_parts.insert(0, msg_text)
            estimated_tokens += msg_tokens

        return "\n".join(context_parts)

    def clear_session(self, session_id: str) -> bool:
        """Clear history for a session."""
        if session_id in self._sessions:
            self._sessions[session_id] = []
            if session_id in self._metadata:
                self._metadata[session_id]["message_count"] = 0
            logger.info(f"Cleared session: {session_id}")
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a session entirely."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            if session_id in self._metadata:
                del self._metadata[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Get metadata about a session."""
        if session_id not in self._sessions:
            return None

        return {
            "session_id": session_id,
            "message_count": len(self._sessions[session_id]),
            **self._metadata.get(session_id, {}),
        }

    def list_sessions(self) -> List[str]:
        """List all active session IDs."""
        return list(self._sessions.keys())
