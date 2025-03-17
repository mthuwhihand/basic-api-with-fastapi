from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

# from app.core.api_response import create_api_response
from app.core.config import settings
import jwt

from app.utils.logger import logger

auth_scheme = HTTPBearer()


async def auth_middleware(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid token",
        )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        request.state.data = payload
        request.state.token = token

    except jwt.ExpiredSignatureError as e:
        logger.info("Auth Middleware: ExpiredSignatureError Error: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError as e:
        logger.info("Auth Middleware: InvalidTokenError Error: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return payload
