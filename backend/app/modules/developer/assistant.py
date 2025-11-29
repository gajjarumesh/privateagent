"""Developer assistant module for code generation and review."""

import logging
import re
from typing import Dict, Any, Optional

from app.core.llm_engine import LLMEngine
from app.security import validate_code_safety

logger = logging.getLogger(__name__)


class DeveloperAssistant:
    """Code generation, review, and debugging assistant."""

    SUPPORTED_LANGUAGES = [
        "python", "javascript", "typescript", "java", "c", "cpp",
        "go", "rust", "ruby", "php", "swift", "kotlin", "sql"
    ]

    def __init__(self, llm: Optional[LLMEngine] = None):
        """Initialize developer assistant."""
        self.llm = llm or LLMEngine()

    async def process(
        self, message: str, context: str = ""
    ) -> Dict[str, Any]:
        """
        Process a developer assistance request.

        Args:
            message: User's request
            context: Conversation context

        Returns:
            Dict with response and metadata
        """
        # Detect the type of request
        request_type = self._detect_request_type(message)
        language = self._detect_language(message)

        system_prompt = self._get_system_prompt(request_type, language)

        prompt = f"""Previous context:
{context}

User request: {message}

Provide a helpful response with:
1. Clear explanation
2. Code examples if appropriate (use markdown code blocks)
3. Best practices and considerations

Response:"""

        result = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4,  # Lower temperature for code
        )

        return result

    def _detect_request_type(self, message: str) -> str:
        """Detect the type of developer request."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["debug", "error", "fix", "bug", "issue"]):
            return "debugging"
        elif any(word in message_lower for word in ["review", "improve", "optimize", "refactor"]):
            return "review"
        elif any(word in message_lower for word in ["explain", "how does", "what is", "understand"]):
            return "explanation"
        elif any(word in message_lower for word in ["generate", "create", "write", "build", "make"]):
            return "generation"
        else:
            return "general"

    def _detect_language(self, message: str) -> str:
        """Detect programming language from message."""
        message_lower = message.lower()

        for lang in self.SUPPORTED_LANGUAGES:
            if lang in message_lower:
                return lang

        # Check for file extensions
        extension_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".java": "java", ".go": "go", ".rs": "rust",
            ".rb": "ruby", ".php": "php", ".sql": "sql"
        }

        for ext, lang in extension_map.items():
            if ext in message_lower:
                return lang

        return "python"  # Default

    def _get_system_prompt(self, request_type: str, language: str) -> str:
        """Get appropriate system prompt based on request type."""
        base_prompt = f"""You are an expert {language} developer and programming assistant.
You provide clear, well-documented, and production-ready code.
Always follow best practices and coding standards for {language}.
Include helpful comments and explain your reasoning."""

        type_additions = {
            "debugging": """
Focus on:
- Identifying the root cause of the issue
- Explaining why the bug occurs
- Providing a corrected solution
- Suggesting preventive measures""",

            "review": """
Focus on:
- Code quality and readability
- Potential bugs or issues
- Performance optimizations
- Security considerations
- Best practice adherence""",

            "generation": """
Focus on:
- Clean, maintainable code
- Proper error handling
- Type hints and documentation
- Following language conventions
- Edge case handling""",

            "explanation": """
Focus on:
- Clear, accessible explanations
- Relevant examples
- Common use cases
- Related concepts and patterns""",
        }

        return base_prompt + type_additions.get(request_type, "")

    async def generate_code(
        self,
        description: str,
        language: str = "python",
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate code based on description."""
        prompt = f"""Generate {language} code for the following:

Description: {description}

Requirements:
1. Write clean, production-ready code
2. Include proper error handling
3. Add comments explaining the logic
4. Follow {language} best practices

{f'Context: {context}' if context else ''}

Code:"""

        result = await self.llm.generate_code(
            prompt=prompt,
            language=language,
        )

        # Validate generated code safety
        code = result.get("response", "")
        is_safe, safety_msg = validate_code_safety(code)

        if not is_safe:
            result["safety_warning"] = safety_msg
            logger.warning(f"Generated code safety warning: {safety_msg}")

        return result

    async def review_code(
        self,
        code: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """Review code and provide feedback."""
        prompt = f"""Review the following {language} code and provide detailed feedback:

```{language}
{code}
```

Provide feedback on:
1. Code quality and readability
2. Potential bugs or issues
3. Performance considerations
4. Security concerns
5. Best practice adherence
6. Suggested improvements

Review:"""

        system_prompt = f"""You are a senior {language} developer conducting a code review.
Be thorough but constructive. Prioritize critical issues.
Provide specific suggestions with code examples when helpful."""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        )

    async def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium",
    ) -> Dict[str, Any]:
        """Explain what code does."""
        detail_instructions = {
            "brief": "Provide a brief, high-level explanation.",
            "medium": "Explain the code step by step with moderate detail.",
            "detailed": "Provide a detailed explanation of every part of the code.",
        }

        prompt = f"""Explain the following {language} code:

```{language}
{code}
```

{detail_instructions.get(detail_level, detail_instructions["medium"])}

Explanation:"""

        return await self.llm.generate(
            prompt=prompt,
            temperature=0.5,
        )

    async def debug_code(
        self,
        code: str,
        error_message: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """Help debug code with an error."""
        prompt = f"""Debug the following {language} code:

Code:
```{language}
{code}
```

Error message:
{error_message}

Please:
1. Identify the cause of the error
2. Explain why it occurs
3. Provide the corrected code
4. Suggest how to prevent similar issues

Debug analysis:"""

        system_prompt = f"""You are an expert {language} debugger.
Be methodical in your analysis. Identify root causes, not just symptoms.
Provide clear explanations and working solutions."""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        )
