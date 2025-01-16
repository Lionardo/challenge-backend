import os
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

JWT_SECRET = "CHANGE_ME"  # For demo only - store securely
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
# Password hashing context (using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash the plain-text password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the given plain-text password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    """
    Create a JWT token with an expiration time.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_session(supabase, user_id: str, token: str) -> dict:
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    response = (
        supabase.table("sessions")
        .insert(
            {"user_id": user_id, "token": token, "expires_at": expires_at.isoformat()}
        )
        .execute()
    )

    return response.data[0]


def verify_session(supabase, token: str) -> Optional[dict]:
    response = (
        supabase.table("sessions")
        .select("*")
        .eq("token", token)
        .gt("expires_at", datetime.now(timezone.utc).isoformat())
        .execute()
    )

    return response.data[0] if response.data else None


def delete_session(supabase, token: str):
    supabase.table("sessions").delete().eq("token", token).execute()
