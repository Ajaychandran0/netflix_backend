from app.server import create_app
from app.core.config.env import settings
import uvicorn

app = create_app()

willReload = settings.APP_ENV != "production"
if __name__ == "__main__":
    uvicorn.run("main:app", port=settings.CONTENT_SERVICE_PORT, host= '0.0.0.0', reload=willReload)