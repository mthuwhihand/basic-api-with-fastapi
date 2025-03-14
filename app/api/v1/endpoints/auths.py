from fastapi import APIRouter, Request
from fastapi.params import Depends
from app.schemas.users import SignIn, SignUp, UserUpdateSchema
from app.services.auth import AuthService
from app.repositories.user import UserRepository
from app.core.database import db
from app.core.middlewares import auth_middleware

routers = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService(UserRepository(db))


@routers.patch("/", dependencies=[Depends(auth_middleware)])
async def update_info(request: Request, data: UserUpdateSchema):
    return auth_service.update_info(request, data)


@routers.delete("/", dependencies=[Depends(auth_middleware)])
async def delete(request: Request, id: str):
    return auth_service.delete(request, id)


@routers.post("/refresh", dependencies=[Depends(auth_middleware)])
async def refresh_access_token(request: Request):
    return auth_service.refresh_access_token(request)


@routers.post("/logout", dependencies=[Depends(auth_middleware)])
async def log_out(request: Request):
    return auth_service.log_out(request)


@routers.post("/login")
async def login(sign_in_rq: SignIn):
    return auth_service.log_in(sign_in_rq)


@routers.post("/register")
async def register(sign_up_rq: SignUp):
    return auth_service.register(sign_up_rq)
