"""Configuration management for ARIA."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Application
    app_name: str = "ARIA"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "change-me-in-production-use-a-secure-key"

    # Database
    database_url: str = "postgresql://aria:aria_password@localhost:5432/aria_db"

    # Ollama LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral:7b-instruct-q4_K_M"
    ollama_code_model: str = "codellama:7b-instruct-q4_K_M"
    ollama_timeout: int = 120

    # Security
    encryption_key: Optional[str] = None
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Memory
    max_conversation_history: int = 20
    max_context_tokens: int = 4096

    # API Keys (for external services - not AI)
    yahoo_finance_enabled: bool = True

    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"


settings = Settings()
