from fastapi import APIRouter

from api.v1.routes import v1_router

api_router = APIRouter(prefix="/api")

routers = [
    v1_router,
]

for router in routers:
    api_router.include_router(router)
