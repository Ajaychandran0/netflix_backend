from fastapi import Depends, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import APIRouter, FastAPI

from app.core.config.env import settings

security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if not (
        credentials.username == settings.API_DOCS_USER
        and credentials.password == settings.API_DOCS_PASS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

def register_docs_routes(app: FastAPI):
    router = APIRouter()

    @router.get("/openapi.json", include_in_schema=False)
    def openapi_endpoint(credentials: HTTPBasicCredentials = Depends(authenticate)):
        return JSONResponse(get_openapi(title=app.title, version=app.version, routes=app.routes))

    @router.get("/docs", include_in_schema=False)
    def swagger_ui(credentials: HTTPBasicCredentials = Depends(authenticate)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title="Docs")

    @router.get("/redoc", include_in_schema=False)
    def redoc_ui(credentials: HTTPBasicCredentials = Depends(authenticate)):
        return get_redoc_html(openapi_url="/openapi.json", title="ReDoc")

    app.include_router(router)
