from fastapi import FastAPI
from app.core.config.env import settings
from app.core.middlewares.cors import add_middlewares
from app.routes.docs import register_docs_routes

def create_app() -> FastAPI:
    is_prod = settings.APP_ENV == "production"
    app = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        port=settings.CONTENT_SERVICE_PORT,
    )

    add_middlewares(app)

    if not is_prod:
        register_docs_routes(app)

    return app
