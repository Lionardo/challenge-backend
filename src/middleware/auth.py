from fastapi import Request, HTTPException, status
from functools import wraps

import supabase
from ..utils.utils import verify_session


def require_auth(func):
    @wraps(func)
    async def wrapper(*args, request: Request, **kwargs):
        access_token = request.cookies.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )

        token = access_token.replace("Bearer ", "")
        session = verify_session(supabase, token)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
            )

        return await func(request=request, **kwargs)

    return wrapper
