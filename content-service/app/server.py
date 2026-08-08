from fastapi import FastAPI

from app.core.middlewares.cors import add_middlewares
from app.core.middlewares.lifespan import lifespan
from app.core.config.env import settings

from app.routes.docs import register_docs_routes
from app.routes.v1.upload import router as upload_router
from app.routes.v1.videos import router as video_router
from app.routes.v1.playback import router as playback_router



def create_app() -> FastAPI:
    is_prod = settings.APP_ENV == "production"
    app: FastAPI = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        title="Content Service API",
        description="API for managing content",
        version="1.0.0",
        lifespan=lifespan,
    )

    add_middlewares(app)

    if not is_prod:
        register_docs_routes(app)

    @app.get("/")
    async def root():
        return {"message": "Welcome to the Content Service API"}

    app.include_router(upload_router, prefix="/api/content", tags=["Uploads"])
    app.include_router(video_router, prefix="/api/content", tags=["Videos"])
    app.include_router(playback_router, prefix="/api/content", tags=["Playback"])


    return app
