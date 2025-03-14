import base64
import uuid
from fastapi import HTTPException, Request
import jwt
import bcrypt
from datetime import datetime, timedelta
from app.core.config import settings
from app.utils.logger import logger


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=5)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(days=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Token is invalid"}


def get_id_from_request(request: Request):
    if not hasattr(request.state, "data"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    id = request.state.data.get("id")
    if not id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return id


def get_token(request: Request):
    if not hasattr(request.state, "token"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return request.state.token


def gen_uuid():
    return str(uuid.uuid4())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def is_valid_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())
