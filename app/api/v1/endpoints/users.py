from fastapi import APIRouter, Request
from fastapi.params import Depends
from app.services.user import UserService
from app.repositories.user import UserRepository
from app.core.database import db
from app.core.middlewares import auth_middleware

routers = APIRouter(prefix="/users", tags=["users"])
user_service = UserService(UserRepository(db))


@routers.get("/", dependencies=[Depends(auth_middleware)])
async def search(request: Request, limit: int = 10, page: int = 1, query: str = ""):
    return user_service.search(request, limit, page, query)
