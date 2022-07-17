import hashlib


def hash_password(password: str) -> str:
    return str(hashlib.sha256(f"{password}".encode()).digest())