"""Ollama LLM integration for local inference."""

import logging
import httpx
from typing import Optional, Dict, Any, AsyncGenerator

from app.config import settings

logger = logging.getLogger(__name__)


class LLMEngine:
    """Local LLM engine using Ollama."""

    def __init__(self):
        """Initialize the LLM engine."""
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.code_model = settings.ollama_code_model
        self.timeout = settings.ollama_timeout

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user's input prompt
            system_prompt: Optional system prompt for context
            model: Model to use (defaults to configured model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with response and metadata
        """
        model = model or self.model
        url = f"{self.base_url}/api/generate"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)

                # Handle specific HTTP status codes
                if response.status_code == 404:
                    logger.error(f"Model '{model}' not found in Ollama")
                    return {
                        "response": f"Model '{model}' not found. Please run 'ollama pull {model}' first.",
                        "model": model,
                        "error": "model_not_found",
                    }

                response.raise_for_status()
                data = response.json()

                return {
                    "response": data.get("response", ""),
                    "model": model,
                    "tokens_used": data.get("eval_count", 0),
                    "done": data.get("done", True),
                }

        except httpx.TimeoutException:
            logger.error("LLM request timed out")
            return {
                "response": "I apologize, but the request timed out. Please try again.",
                "model": model,
                "error": "timeout",
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM HTTP status error: {e.response.status_code}")
            if e.response.status_code == 500:
                return {
                    "response": "Ollama encountered a server error. Please try again.",
                    "model": model,
                    "error": "server_error",
                }
            return {
                "response": f"HTTP error occurred: {e.response.status_code}",
                "model": model,
                "error": str(e),
            }
        except httpx.HTTPError as e:
            logger.error(f"LLM HTTP error: {str(e)}")
            return {
                "response": "I encountered an error. Please ensure Ollama is running.",
                "model": model,
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return {
                "response": "An unexpected error occurred.",
                "model": model,
                "error": str(e),
            }

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response from the LLM."""
        model = model or self.model
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, json=payload) as response:
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                            if data.get("done"):
                                break
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"Error: {str(e)}"

    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate code using the code-specialized model."""
        system_prompt = f"""You are an expert {language} programmer. 
Generate clean, well-documented, and efficient code.
Always include comments explaining the logic.
Follow best practices and coding standards for {language}."""

        if context:
            prompt = f"Context:\n{context}\n\nRequest:\n{prompt}"

        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model=self.code_model,
            temperature=0.3,  # Lower temperature for more deterministic code
        )

    async def check_health(self) -> bool:
        """Check if Ollama is running and responsive."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list:
        """List available models in Ollama."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
        return []
