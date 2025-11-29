"""Input validation utilities."""

import re
from typing import Optional, Tuple


def validate_session_id(session_id: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a session ID.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not session_id:
        return False, "Session ID cannot be empty"

    if len(session_id) > 100:
        return False, "Session ID too long"

    # Allow alphanumeric, underscore, hyphen
    if not re.match(r"^[a-zA-Z0-9_-]+$", session_id):
        return False, "Session ID contains invalid characters"

    return True, None


def validate_message(message: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a chat message.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message:
        return False, "Message cannot be empty"

    if len(message) > 10000:
        return False, "Message too long (max 10000 characters)"

    # Check for null bytes
    if "\x00" in message:
        return False, "Message contains invalid characters"

    return True, None


def validate_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a trading symbol.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not symbol:
        return False, "Symbol cannot be empty"

    if len(symbol) > 10:
        return False, "Symbol too long"

    # Allow alphanumeric, dot, hyphen (for crypto pairs)
    if not re.match(r"^[A-Za-z0-9.-]+$", symbol):
        return False, "Symbol contains invalid characters"

    return True, None


def validate_code(code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate code input for safety.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not code:
        return False, "Code cannot be empty"

    if len(code) > 50000:
        return False, "Code too long (max 50000 characters)"

    # Check for null bytes
    if "\x00" in code:
        return False, "Code contains invalid characters"

    return True, None


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage."""
    # Remove path separators
    filename = filename.replace("/", "_").replace("\\", "_")

    # Remove special characters
    filename = re.sub(r"[^\w.-]", "_", filename)

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:255-len(ext)-1] + "." + ext if ext else name[:255]

    return filename


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an email address.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email cannot be empty"

    if len(email) > 254:
        return False, "Email too long"

    # Basic email pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Invalid email format"

    return True, None
