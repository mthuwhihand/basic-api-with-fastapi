from typing import Optional
import uuid
from fastapi import HTTPException, Request
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from app.core.config import settings


def create_access_token(
    data: dict, expires_delta: int = settings.ACCESS_TOKEN_EXPIRES_IN
):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    create_at = datetime.now(timezone.utc)

    to_encode.update(
        {"exp": int(expire.timestamp()), "create_at": int(create_at.timestamp())}
    )

    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(data: dict, exp: Optional[datetime] = None):
    to_encode = data.copy()
    if exp is None:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRES_IN
        )
        exp = int(expire.timestamp())
    elif isinstance(exp, datetime):
        exp = int(exp.timestamp())

    create_at = int(datetime.now(timezone.utc).timestamp())

    to_encode.update({"exp": exp, "create_at": create_at})
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
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


def get_field_data_from_request(request: Request, field: str):
    if not hasattr(request.state, "data"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    field_data = request.state.data.get(field)
    if not field_data:
        return None
    return field_data


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
