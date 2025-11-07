"""Security and encryption utilities for the backend."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from typing import Optional


def generate_salt(length: int = 16) -> str:
    """Generate a cryptographically secure random salt."""
    if length <= 0:
        raise ValueError("Salt length must be positive")
    return base64.urlsafe_b64encode(os.urandom(length)).decode("utf-8")


def hash_text(text: str, *, salt: Optional[str] = None, iterations: int = 100_000) -> str:
    """Hash text using PBKDF2-HMAC-SHA256.

    Returns the hash in the format ``salt$iterations$hash``.
    """

    if not text:
        raise ValueError("Text to hash must not be empty")

    salt_value = salt or generate_salt()
    dk = hashlib.pbkdf2_hmac("sha256", text.encode("utf-8"), salt_value.encode("utf-8"), iterations)
    hashed = base64.urlsafe_b64encode(dk).decode("utf-8")
    return f"{salt_value}${iterations}${hashed}"


def verify_hash(text: str, stored_hash: str) -> bool:
    """Verify that the provided text matches the stored hash."""

    try:
        salt, iterations_str, hashed = stored_hash.split("$")
        iterations = int(iterations_str)
    except ValueError:
        raise ValueError("Stored hash has invalid format. Expected 'salt$iterations$hash'.")

    calculated = hash_text(text, salt=salt, iterations=iterations)
    return hmac.compare_digest(calculated, f"{salt}${iterations}${hashed}")


def generate_hmac(message: str, secret_key: str, *, algorithm: str = "sha256") -> str:
    """Generate an HMAC signature for a message."""

    if not message:
        raise ValueError("Message must not be empty")
    if not secret_key:
        raise ValueError("Secret key must not be empty")

    digest = hmac.new(
        secret_key.encode("utf-8"), message.encode("utf-8"), getattr(hashlib, algorithm)
    )
    return base64.urlsafe_b64encode(digest.digest()).decode("utf-8")


def _derive_fernet_key(secret_key: str) -> bytes:
    """Derive a Fernet-compatible key from an arbitrary secret."""
    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_text(plain_text: str, secret_key: str) -> str:
    """Encrypt text using Fernet symmetric encryption.

    Requires the ``cryptography`` package to be installed.
    """

    if not plain_text:
        raise ValueError("Plain text must not be empty")
    if not secret_key:
        raise ValueError("Secret key must not be empty")

    try:
        from cryptography.fernet import Fernet
    except ImportError as exc:  # pragma: no cover - defensive branch
        raise RuntimeError(
            "cryptography package is required for encryption utilities. Install it with 'pip install cryptography'."
        ) from exc

    fernet = Fernet(_derive_fernet_key(secret_key))
    return fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")


def decrypt_text(token: str, secret_key: str) -> str:
    """Decrypt text previously encrypted with ``encrypt_text``."""

    if not token:
        raise ValueError("Token must not be empty")
    if not secret_key:
        raise ValueError("Secret key must not be empty")

    try:
        from cryptography.fernet import Fernet
    except ImportError as exc:  # pragma: no cover - defensive branch
        raise RuntimeError(
            "cryptography package is required for encryption utilities. Install it with 'pip install cryptography'."
        ) from exc

    fernet = Fernet(_derive_fernet_key(secret_key))
    return fernet.decrypt(token.encode("utf-8")).decode("utf-8")


__all__ = [
    "generate_salt",
    "hash_text",
    "verify_hash",
    "generate_hmac",
    "encrypt_text",
    "decrypt_text",
]
