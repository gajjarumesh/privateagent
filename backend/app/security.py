"""Security utilities for ARIA."""

import re
import secrets
from typing import Optional, Tuple
from cryptography.fernet import Fernet

from app.config import settings


def get_encryption_key() -> bytes:
    """Get or generate encryption key."""
    if settings.encryption_key:
        return settings.encryption_key.encode()
    # Generate a new key if not provided
    return Fernet.generate_key()


_fernet: Optional[Fernet] = None


def get_fernet() -> Fernet:
    """Get Fernet instance for encryption/decryption."""
    global _fernet
    if _fernet is None:
        _fernet = Fernet(get_encryption_key())
    return _fernet


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data."""
    fernet = get_fernet()
    return fernet.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    fernet = get_fernet()
    return fernet.decrypt(encrypted_data.encode()).decode()


def generate_session_id() -> str:
    """Generate a secure session ID."""
    return secrets.token_urlsafe(32)


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text:
        return ""

    # Remove potentially dangerous characters and patterns
    # Remove null bytes
    text = text.replace("\x00", "")

    # Limit length to prevent DoS
    max_length = 10000
    if len(text) > max_length:
        text = text[:max_length]

    # Remove control characters except newlines and tabs
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    return text.strip()


def validate_code_safety(code: str) -> Tuple[bool, str]:
    """
    Validate code for potentially dangerous operations.

    Returns:
        Tuple of (is_safe, message)
    """
    dangerous_patterns = [
        (r"\bos\.system\b", "os.system calls are not allowed"),
        (r"\bsubprocess\b", "subprocess module is not allowed"),
        (r"\beval\b", "eval() is not allowed"),
        (r"\bexec\b", "exec() is not allowed"),
        (r"\b__import__\b", "__import__ is not allowed"),
        (r"\bopen\s*\([^)]*['\"]w", "Writing files is not allowed"),
        (r"\brm\s+-rf\b", "Destructive commands are not allowed"),
        (r"\bshutil\.rmtree\b", "Recursive deletion is not allowed"),
    ]

    for pattern, message in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return False, message

    return True, "Code appears safe"
