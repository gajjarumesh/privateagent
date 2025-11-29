"""Main agent orchestrator."""

import logging
from typing import Dict, Any, Optional

from app.core.llm_engine import LLMEngine
from app.core.memory import ConversationMemory
from app.modules.developer.assistant import DeveloperAssistant
from app.modules.trading.analyst import TradingAnalyst
from app.modules.research.engine import ResearchEngine
from app.security import generate_session_id

logger = logging.getLogger(__name__)


class Agent:
    """Main agent that orchestrates all modules."""

    def __init__(self, llm_engine: Optional[LLMEngine] = None):
        """Initialize the agent."""
        self.llm = llm_engine or LLMEngine()
        self.memory = ConversationMemory()

        # Initialize specialized modules
        self._developer = None
        self._trading = None
        self._research = None

    @property
    def developer(self) -> DeveloperAssistant:
        """Get developer assistant module."""
        if self._developer is None:
            self._developer = DeveloperAssistant(self.llm)
        return self._developer

    @property
    def trading(self) -> TradingAnalyst:
        """Get trading analyst module."""
        if self._trading is None:
            self._trading = TradingAnalyst(self.llm)
        return self._trading

    @property
    def research(self) -> ResearchEngine:
        """Get research engine module."""
        if self._research is None:
            self._research = ResearchEngine(self.llm)
        return self._research

    async def process(
        self,
        message: str,
        session_id: Optional[str] = None,
        module: str = "general",
    ) -> Dict[str, Any]:
        """
        Process a user message and route to appropriate module.

        Args:
            message: User's input message
            session_id: Optional existing session ID
            module: Target module (general, developer, trading, research)

        Returns:
            Dict with response and metadata
        """
        # Create or use existing session
        if not session_id:
            session_id = self.memory.create_session()
        elif session_id not in self.memory._sessions:
            self.memory.create_session(session_id)

        # Store user message
        message_id = self.memory.add_message(
            session_id=session_id,
            role="user",
            content=message,
            metadata={"module": module},
        )

        # Get conversation context
        context = self.memory.get_context(session_id)

        # Route to appropriate module
        try:
            if module == "developer":
                response = await self._handle_developer(message, context)
            elif module == "trading":
                response = await self._handle_trading(message, context)
            elif module == "research":
                response = await self._handle_research(message, context)
            else:
                response = await self._handle_general(message, context)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            response = {
                "response": "I encountered an error processing your request. Please try again.",
                "error": str(e),
            }

        # Store assistant response
        self.memory.add_message(
            session_id=session_id,
            role="assistant",
            content=response["response"],
            metadata={"module": module, "tokens_used": response.get("tokens_used")},
        )

        return {
            "response": response["response"],
            "session_id": session_id,
            "message_id": message_id,
            "tokens_used": response.get("tokens_used"),
            "module": module,
        }

    async def _handle_general(
        self, message: str, context: str
    ) -> Dict[str, Any]:
        """Handle general chat messages."""
        system_prompt = """You are ARIA, an Adaptive Research & Intelligence Agent.
You are a helpful, friendly AI assistant running locally on the user's machine.
You have specialized modules for:
- Development assistance (code generation, debugging, best practices)
- Market trading analysis (technical indicators, price analysis)
- Research (web search, document analysis)

For specialized tasks, suggest the user switch to the appropriate module.
Be concise, helpful, and friendly."""

        prompt = f"Previous context:\n{context}\n\nUser: {message}\n\nAssistant:"

        result = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return result

    async def _handle_developer(
        self, message: str, context: str
    ) -> Dict[str, Any]:
        """Handle developer assistant requests."""
        return await self.developer.process(message, context)

    async def _handle_trading(
        self, message: str, context: str
    ) -> Dict[str, Any]:
        """Handle trading analysis requests."""
        return await self.trading.process(message, context)

    async def _handle_research(
        self, message: str, context: str
    ) -> Dict[str, Any]:
        """Handle research requests."""
        return await self.research.process(message, context)

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all components."""
        llm_healthy = await self.llm.check_health()

        return {
            "status": "healthy" if llm_healthy else "degraded",
            "llm": {"status": "healthy" if llm_healthy else "unavailable"},
            "memory": {"sessions": len(self.memory.list_sessions())},
        }
