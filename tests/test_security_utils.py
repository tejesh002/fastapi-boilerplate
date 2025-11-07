"""Tests for security utility helpers."""

import base64
import importlib.util

import pytest

from src.utils import security


CRYPTOGRAPHY_AVAILABLE = importlib.util.find_spec("cryptography") is not None


class TestSaltGeneration:
    def test_generate_salt_has_expected_properties(self):
        salt = security.generate_salt(32)

        assert isinstance(salt, str)
        assert len(salt) > 0
        # Round-trip through base64 to ensure it is valid
        base64.urlsafe_b64decode(salt.encode("utf-8"))

    def test_generate_salt_rejects_non_positive_length(self):
        with pytest.raises(ValueError):
            security.generate_salt(0)


class TestHashing:
    def test_hash_text_includes_salt_iteration_and_hash(self):
        hashed = security.hash_text("secret", salt="fixed_salt", iterations=10)

        salt, iterations, digest = hashed.split("$")
        assert salt == "fixed_salt"
        assert iterations == "10"
        assert len(digest) > 10

    def test_hash_text_rejects_empty_value(self):
        with pytest.raises(ValueError):
            security.hash_text("")

    def test_verify_hash_matches_original_text(self):
        hashed = security.hash_text("password123")

        assert security.verify_hash("password123", hashed)
        assert not security.verify_hash("other", hashed)

    def test_verify_hash_invalid_format(self):
        with pytest.raises(ValueError):
            security.verify_hash("value", "not-a-valid-hash")


class TestHmac:
    def test_generate_hmac_is_deterministic(self):
        signature = security.generate_hmac("message", "key")
        assert signature == security.generate_hmac("message", "key")

    def test_generate_hmac_rejects_missing_inputs(self):
        with pytest.raises(ValueError):
            security.generate_hmac("", "key")
        with pytest.raises(ValueError):
            security.generate_hmac("message", "")


@pytest.mark.skipif(
    not CRYPTOGRAPHY_AVAILABLE, reason="cryptography package is required for encryption tests"
)
class TestSymmetricEncryption:
    def test_encrypt_then_decrypt_roundtrip(self):
        secret_key = "super-secret"
        ciphertext = security.encrypt_text("payload", secret_key)

        assert security.decrypt_text(ciphertext, secret_key) == "payload"

    def test_encrypt_text_rejects_invalid_inputs(self):
        with pytest.raises(ValueError):
            security.encrypt_text("", "key")
        with pytest.raises(ValueError):
            security.encrypt_text("payload", "")

    def test_decrypt_text_rejects_invalid_inputs(self):
        with pytest.raises(ValueError):
            security.decrypt_text("", "key")
        with pytest.raises(ValueError):
            security.decrypt_text("token", "")
