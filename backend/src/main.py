from pathlib import Path

from fastapi import Depends, FastAPI
from uvicorn import run as server_start

from api.routes import api_router
from core.config import host_settings
from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper

app = FastAPI(
    openapi_url="/api/openapi.json",
    docs_url="/api/openapi",
    redoc_url="/api/redocapi",
)

app.include_router(api_router)

logger = get_configure_logger(Path(__file__).stem)


if __name__ == "__main__":
    server_start(
        "main:app",
        reload=host_settings.is_reload,
        host=host_settings.host,
        port=host_settings.port,
    )
