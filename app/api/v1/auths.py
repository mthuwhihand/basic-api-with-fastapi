from fastapi import APIRouter, Form, Request
from fastapi.params import Depends
from pydantic import EmailStr
from app.schemas.users import SignIn, SignUp, UserUpdateSchema
from app.services import auth as auth_service
from app.core.middlewares import auth_middleware
from app.utils.logger import logger

routers = APIRouter(prefix="/auth", tags=["auth"])


@routers.patch("", dependencies=[Depends(auth_middleware)])
async def update_info(request: Request, data: UserUpdateSchema):
    return auth_service.update_info(request, data)


@routers.delete("", dependencies=[Depends(auth_middleware)])
async def delete(request: Request, id: str):
    return auth_service.delete(request, id)


@routers.post("/refresh", dependencies=[Depends(auth_middleware)])
async def refresh_access_token(request: Request):
    return auth_service.refresh_access_token(request)


@routers.get("/get-data", dependencies=[Depends(auth_middleware)])
async def get_data(request: Request):
    return auth_service.get_data(request)


@routers.post("/logout", dependencies=[Depends(auth_middleware)])
async def logout(request: Request):
    return auth_service.logout(request)


@routers.post("/login")
async def login(sign_in_rq: SignIn):
    return auth_service.login(sign_in_rq)


@routers.post("/register")
async def register(sign_up_rq: SignUp):
    return auth_service.register(sign_up_rq)


@routers.post("/forget-password", tags=["send-mail"])
async def forget_password(request: Request, email: EmailStr):
    return await auth_service.forget_password(request, email)


@routers.get("/form/reset-password")
async def send_form_reset_password(request: Request, name: str, email: str, token: str):
    return auth_service.send_form_reset_password(request, name, email, token)


@routers.post("/reset-password")
async def reset_password(request: Request, token: str, password: str = Form()):
    return auth_service.reset_password(request, token, password)
