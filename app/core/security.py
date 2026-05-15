from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from app.core.config import get_settings

_PASSWORD_ALGORITHM = "pbkdf2_sha256"
_PASSWORD_ITERATIONS = 120_000


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def get_password_hash(password: str, *, salt: str | None = None) -> str:
    normalized = password.encode("utf-8")
    raw_salt = salt or secrets.token_urlsafe(18)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        normalized,
        raw_salt.encode("utf-8"),
        _PASSWORD_ITERATIONS,
    )
    return f"{_PASSWORD_ALGORITHM}${_PASSWORD_ITERATIONS}${raw_salt}${_b64url_encode(digest)}"


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt, expected_digest = password_hash.split("$", 3)
        iterations = int(iterations_text)
    except ValueError:
        return False

    if algorithm != _PASSWORD_ALGORITHM:
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return hmac.compare_digest(_b64url_encode(digest), expected_digest)


def _token_signature(payload_part: str) -> str:
    key = get_settings().auth_secret.encode("utf-8")
    return _b64url_encode(hmac.new(key, payload_part.encode("ascii"), hashlib.sha256).digest())


def create_access_token(subject: str, *, expires_seconds: int | None = None) -> str:
    settings = get_settings()
    now = int(time.time())
    expires_in = expires_seconds or settings.access_token_expire_seconds
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + int(expires_in),
    }
    payload_part = _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    return f"{payload_part}.{_token_signature(payload_part)}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload_part, signature = token.split(".", 1)
    except ValueError as exc:
        raise ValueError("invalid token format") from exc

    expected_signature = _token_signature(payload_part)
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("invalid token signature")

    try:
        payload = json.loads(_b64url_decode(payload_part).decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid token payload") from exc

    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        raise ValueError("token expired")

    return payload


__all__ = [
    "create_access_token",
    "decode_access_token",
    "get_password_hash",
    "verify_password",
]
