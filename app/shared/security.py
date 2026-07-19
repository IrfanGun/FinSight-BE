import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from typing import Any


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1)
    encoded_salt = base64.b64encode(salt).decode("utf-8")
    encoded_key = base64.b64encode(derived_key).decode("utf-8")
    return f"{encoded_salt}${encoded_key}"


def verify_password(password: str, hashed_password: str) -> bool:
    encoded_salt, encoded_key = hashed_password.split("$", maxsplit=1)
    salt = base64.b64decode(encoded_salt.encode("utf-8"))
    expected_key = base64.b64decode(encoded_key.encode("utf-8"))
    actual_key = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1)
    return hmac.compare_digest(actual_key, expected_key)


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("utf-8"))


def _json_default(value: Any):
    if isinstance(value, datetime):
        return int(value.timestamp())
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def create_jwt_token(payload: dict[str, Any], secret_key: str) -> str:
    header = {
        "alg": "HS256",
        "typ": "JWT",
    }
    encoded_header = _base64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    encoded_payload = _base64url_encode(
        json.dumps(payload, default=_json_default, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    return f"{encoded_header}.{encoded_payload}.{_base64url_encode(signature)}"


def decode_jwt_token(token: str, secret_key: str) -> dict[str, Any]:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
    except ValueError as exc:
        raise ValueError("Invalid token format") from exc

    header = json.loads(_base64url_decode(encoded_header))
    if header.get("alg") != "HS256":
        raise ValueError("Invalid token algorithm")

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    expected_signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    actual_signature = _base64url_decode(encoded_signature)
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise ValueError("Invalid token signature")

    payload = json.loads(_base64url_decode(encoded_payload))
    expires_at = payload.get("exp")
    if expires_at is not None and datetime.now(timezone.utc).timestamp() > expires_at:
        raise ValueError("Token has expired")

    return payload
