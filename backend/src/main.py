from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from uvicorn import run as server_start

from api.routes import api_router
from core.config import host_settings
from core.logger.logger import get_configure_logger
from db.dependencies.base_statements import BASE_STATEMENTS
from db.dependencies.postgres_helper import postgres_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    await postgres_helper.insert_data(BASE_STATEMENTS)
    yield
    await postgres_helper.close_connection()


app = FastAPI(
    openapi_url="/api/openapi.json",
    docs_url="/api/openapi",
    redoc_url="/api/redocapi",
    lifespan=lifespan,
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
