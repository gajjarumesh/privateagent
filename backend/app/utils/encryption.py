"""Data encryption utilities."""

import base64
import secrets
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import settings


class EncryptionManager:
    """Manages encryption and decryption of sensitive data."""

    def __init__(self, key: Optional[str] = None):
        """
        Initialize encryption manager.

        Args:
            key: Optional encryption key. If not provided, uses settings.
        """
        self._key = key or settings.encryption_key
        self._fernet: Optional[Fernet] = None

    def _get_fernet(self) -> Fernet:
        """Get or create Fernet instance."""
        if self._fernet is None:
            if self._key:
                # Use provided key
                key_bytes = self._key.encode() if isinstance(self._key, str) else self._key
                self._fernet = Fernet(key_bytes)
            else:
                # Generate a key from secret
                key = self._derive_key(settings.secret_key)
                self._fernet = Fernet(key)
        return self._fernet

    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """Derive a Fernet key from a password."""
        if salt is None:
            salt = b"aria_salt_v1"  # Static salt for reproducibility

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, data: str) -> str:
        """Encrypt a string."""
        fernet = self._get_fernet()
        encrypted = fernet.encrypt(data.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string."""
        fernet = self._get_fernet()
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()

    def encrypt_dict(self, data: dict) -> str:
        """Encrypt a dictionary as JSON."""
        import json
        json_str = json.dumps(data)
        return self.encrypt(json_str)

    def decrypt_dict(self, encrypted_data: str) -> dict:
        """Decrypt to a dictionary."""
        import json
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)

    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key."""
        return Fernet.generate_key().decode()

    @staticmethod
    def generate_random_token(length: int = 32) -> str:
        """Generate a random token."""
        return secrets.token_urlsafe(length)


# Global encryption manager instance
encryption_manager = EncryptionManager()
