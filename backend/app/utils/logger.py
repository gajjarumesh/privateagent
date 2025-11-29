"""Audit logging utilities."""

import logging
import sys
from datetime import datetime
from typing import Optional, Any
from pathlib import Path

from app.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Set specific log levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.debug else logging.WARNING
    )

    logging.info("Logging configured")


class AuditLogger:
    """Handles audit logging for security-sensitive operations."""

    def __init__(self, name: str = "aria.audit"):
        """Initialize audit logger."""
        self.logger = logging.getLogger(name)
        self._setup_audit_handler()

    def _setup_audit_handler(self) -> None:
        """Set up file handler for audit logs."""
        # In production, this would write to a secure log file
        # For now, we'll use the standard logger
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - AUDIT - %(levelname)s - %(message)s"
            )
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[dict] = None,
        level: str = "info",
    ) -> None:
        """
        Log an audit event.

        Args:
            action: The action performed (e.g., "create", "read", "update", "delete")
            resource_type: Type of resource (e.g., "conversation", "feedback")
            resource_id: Optional ID of the resource
            user_id: Optional user identifier
            ip_address: Optional client IP address
            details: Optional additional details
            level: Log level ("info", "warning", "error")
        """
        message = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details,
        }

        log_method = getattr(self.logger, level, self.logger.info)
        log_method(f"AUDIT: {message}")

    def log_access(
        self,
        endpoint: str,
        method: str,
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Log an API access event."""
        self.log(
            action=f"{method} {endpoint}",
            resource_type="api",
            ip_address=ip_address,
            user_id=user_id,
        )

    def log_security_event(
        self,
        event_type: str,
        description: str,
        ip_address: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        """Log a security-related event."""
        self.log(
            action=event_type,
            resource_type="security",
            ip_address=ip_address,
            details={"description": description, **(details or {})},
            level="warning",
        )


# Global audit logger instance
audit_logger = AuditLogger()
