import os
from fastapi import FastAPI, HTTPException, status, Request
from supabase import create_client, Client
from passlib.context import CryptContext
from dotenv import load_dotenv
from .models.models import SignupRequest, LoginRequest, TokenResponse
from .utils.utils import (
    create_session,
    delete_session,
    hash_password,
    verify_password,
    create_access_token,
    verify_session,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Response
from datetime import datetime, timedelta, timezone
import uvicorn

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/v1/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest):
    """
    Create a new user.
    """
    # Check if user already exists
    existing_user = (
        supabase.table("users").select("*").eq("email", payload.email).execute()
    )
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists.",
        )

    # Hash the password
    password_hash = hash_password(payload.password)

    try:
        # Insert new user into Supabase
        response = (
            supabase.table("users")
            .insert(
                {
                    "email": payload.email,
                    "name": payload.name,
                    "password_hash": password_hash,
                }
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user: No data returned",
            )

        return {"message": "Successfull"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


@app.post("/v1/auth/login", response_model=TokenResponse)
async def login(request: Request, payload: LoginRequest, response: Response):
    """
    Authenticate an existing user and return a JWT token.
    """
    # Check if user exists
    user_response = (
        supabase.table("users").select("*").eq("email", payload.email).execute()
    )
    user_data = user_response.data

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    user = user_data[0]

    # Verify password
    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Create JWT token
    access_token = create_access_token(data={"sub": user["email"]})
    create_session(supabase, user["id"], access_token)

    # Set cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        path="/",
        expires=datetime.now(timezone.utc) + timedelta(days=7),
    )

    return {"message": "Successfull", "token": access_token}


@app.post("/v1/auth/check")
async def check_auth(request: Request, payload: dict):
    """Check if user is authenticated"""

    access_token = payload["token"]
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    session = verify_session(supabase, access_token)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
        )
    print("Session verified")
    return {"authenticated": True}


@app.post("/v1/auth/logout")
async def logout(request: Request, response: Response, payload: dict):
    """
    Logout user and clear session
    """
    access_token = (
        payload["token"]
        if ENVIRONMENT == "development"
        else request.cookies.get("access_token")
    )
    if access_token:
        delete_session(supabase, access_token)

    response.delete_cookie(
        key="access_token", httponly=True, secure=False, samesite="lax", path="/"
    )

    return {"message": "Successfull"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
