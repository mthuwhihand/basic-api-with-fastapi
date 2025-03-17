from app.core.database import engine
from fastapi import APIRouter, FastAPI
from app.utils.logger import logger
from app.api.v1 import auths, users
from fastapi.staticfiles import StaticFiles


routers = APIRouter(
    prefix="/v1",
)

routers.include_router(auths.routers)
routers.include_router(users.routers)


def shutdown_application():
    engine.dispose()
    logger.info("Closed PostgreSQL connection successfully")


def start_application():
    app = FastAPI()
    app.include_router(routers)

    @app.on_event("shutdown")
    async def shutdown():
        shutdown_application()

    return app


app = start_application()
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")


@app.get("/")
async def root():
    return {"message": "Hello World"}
