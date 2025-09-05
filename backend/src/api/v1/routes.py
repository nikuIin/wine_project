from fastapi import APIRouter

from api.v1.endpoints.article import router as article_router
from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.content import router as content_router
from api.v1.endpoints.country import router as country_router
from api.v1.endpoints.deal import router as deal_router
from api.v1.endpoints.grape import router as grape_router
from api.v1.endpoints.partners import router as partners_router
from api.v1.endpoints.region import router as region_router

v1_router = APIRouter(prefix="/v1")


routers = [
    article_router,
    auth_router,
    country_router,
    region_router,
    grape_router,
    content_router,
    deal_router,
    partners_router,
]

for router in routers:
    v1_router.include_router(router)
