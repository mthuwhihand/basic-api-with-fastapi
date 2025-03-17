from fastapi import APIRouter, Request
from fastapi.params import Depends
from app.core.middlewares import auth_middleware
from app.services import user as user_service

routers = APIRouter(prefix="/users", tags=["users"])


@routers.get("", dependencies=[Depends(auth_middleware)])
async def search(request: Request, limit: int = 10, page: int = 1, query: str = ""):
    return user_service.search(request, limit, page, query)
