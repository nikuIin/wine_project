from functools import wraps

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from domain.exceptions import PartnerDatabaseError
from schemas.partner_schema import PartnerSchema, PartnersSchemaResponse
from schemas.support_schemas import LimitSchema, OffsetSchema
from services.partner_service import PartnerService, partner_service_dependency

router = APIRouter(tags=["partners"], prefix="/partner")


def partner_handle(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except PartnerDatabaseError as error:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error.",
            ) from error

    return wrapper


@router.get("/all")
@partner_handle
async def get_all_partners(
    limit: LimitSchema = Depends(),
    offset: OffsetSchema = Depends(),
    partner_service: PartnerService = Depends(partner_service_dependency),
):
    partners = await partner_service.get_partners(int(limit), int(offset))

    return PartnersSchemaResponse(
        partners=[
            PartnerSchema(**partner.model_dump()) for partner in partners
        ]
    )
