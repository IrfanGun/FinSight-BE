import base64
import hashlib
import hmac
import os


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
