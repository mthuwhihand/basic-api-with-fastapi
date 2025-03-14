from app.core.database import engine
from fastapi import FastAPI
from app.utils import logger
from app.api.v1.routes import routers


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


@app.get("/")
async def root():
    return {"message": "Hello World"}
