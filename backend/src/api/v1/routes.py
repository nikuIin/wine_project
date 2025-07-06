from fastapi import APIRouter

from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.country import router as country_router
from api.v1.endpoints.grape import router as grape_router
from api.v1.endpoints.region import router as region_router

v1_router = APIRouter(prefix="/v1")


routers = [
    auth_router,
    country_router,
    region_router,
    grape_router,
]

for router in routers:
    v1_router.include_router(router)
