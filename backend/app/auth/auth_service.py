
"""Password hashing and JWT token utilities."""
from pathlib import Path
from dotenv import load_dotenv

import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

password_hash = PasswordHash.recommended()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_secret_key():
    secret_key = os.getenv("AUTH_SECRET_KEY")

    if not secret_key:
        raise RuntimeError(
            "AUTH_SECRET_KEY environment variable is not configured."
        )

    return secret_key


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(recruiter_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(recruiter_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        get_secret_key(),
        algorithm=ALGORITHM
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            get_secret_key(),
            algorithms=[ALGORITHM]
        )

        recruiter_id = payload.get("sub")

        if not recruiter_id:
            return None

        return int(recruiter_id)

    except (JWTError, ValueError, TypeError):
        return None
