from fastapi import APIRouter
from app.api.v1.endpoints import auths
from app.api.v1.endpoints import users

routers = APIRouter(tags=["v1"])

routers.include_router(auths.routers)
routers.include_router(users.routers)