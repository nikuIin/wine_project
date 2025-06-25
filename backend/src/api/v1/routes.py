from fastapi import APIRouter

from api.v1.endpoints.auth import router as auth_router

v1_router = APIRouter(prefix="/v1")


routers = [
    auth_router,
]

for router in routers:
    v1_router.include_router(router)
