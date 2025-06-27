import uvicorn
from app.server import create_app
from app.core.config.env import settings
from app.core.config.logging import setup_logging

# Initialize logging
setup_logging()

# Create the FastAPI application instance
app = create_app()

willReload = settings.APP_ENV != "production"
if __name__ == "__main__":
    uvicorn.run("main:app", port=settings.CONTENT_SERVICE_PORT, host= '0.0.0.0', reload=willReload)