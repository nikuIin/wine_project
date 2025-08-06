from functools import wraps
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from api.v1.depends import auth_dependency
from core.general_constants import MAX_DB_INT
from domain.entities.deal import Deal
from domain.entities.token import TokenPayload
from domain.exceptions import (
    DealAlreadyExistsError,
    DealDBError,
    DealError,
    DealLeadNotFoundError,
    DealLostReasonNotFoundError,
    DealManagerNotFoundError,
    DealNotFoundError,
    DealSaleStageNotFoundError,
    MessageAlreadyExistsError,
    UserNotFoundError,
)
from dto.deal_dto import DealShortDTO
from schemas.deal_schema import (
    DealCreateSchema,
    DealResponseSchema,
    DealShortResponseSchema,
    DealUpdateSchema,
    LostCreateSchema,
    LostResponseSchema,
)
from schemas.message_schema import MessageCreateSchema, MessageResponseSchema
from schemas.support_schemas import LimitSchema, OffsetSchema
from services.abc.deal_service_abc import AbstractDealService
from services.deal_service import deal_service_dependency

router = APIRouter(prefix="/deal", tags=["deal"])


def get_deal_response(deal: Deal | None) -> DealResponseSchema:
    if deal:
        return DealResponseSchema(
            deal_id=deal.deal_id,
            manager_id=deal.manager_id,
            lead_id=deal.lead_id,
            fields=deal.fields if deal.fields else {},
            cost=deal.cost,
            probability=deal.probability,
            priority=deal.priority,
            created_at=deal.created_at,
            close_at=deal.close_at,
            lost=LostResponseSchema(
                lost_reason=deal.lost_reason,
                description=deal.lost_reason_description,
            )
            if deal.lost_reason
            else None,
        )
    raise HTTPException(
        status_code=HTTP_404_NOT_FOUND,
        detail="Deal doesn't exists",
    )


def handle_deal_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (
            DealLeadNotFoundError,
            DealManagerNotFoundError,
            DealSaleStageNotFoundError,
            DealLostReasonNotFoundError,
            DealNotFoundError,
            UserNotFoundError,
        ) as error:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail=str(error)
            ) from error
        except (DealAlreadyExistsError, MessageAlreadyExistsError) as error:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT, detail=str(error)
            ) from error
        except (DealError, DealDBError) as error:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
            ) from error

    return wrapper


@router.post("/")
@handle_deal_errors
async def create_deal(
    deal_create_data: DealCreateSchema = Body(),
    deal_service: AbstractDealService = Depends(deal_service_dependency),
):
    deal_id = await deal_service.create(deal_create_data)
    return {
        "status": "success",
        "detail": "The deal create successfully!",
        "deal_id": deal_id,
    }


@router.get("/all", response_model=list[DealShortResponseSchema])
async def get_deals(
    limit: LimitSchema = Depends(),
    offset: OffsetSchema = Depends(),
    deal_service: AbstractDealService = Depends(deal_service_dependency),
):
    deals: list[DealShortDTO] = await deal_service.get_deals(
        limit=int(limit),
        offset=int(offset),
    )

    deals_response = [
        DealShortResponseSchema(**deal.model_dump()) for deal in deals
    ]

    return deals_response


@router.get("/{deal_id}/messages")
@handle_deal_errors
async def get_deal_messages(
    deal_id: UUID,
    limit: LimitSchema = Depends(),
    offset: OffsetSchema = Depends(),
    deal_service: AbstractDealService = Depends(deal_service_dependency),
):
    messages = await deal_service.get_messages(
        deal_id=deal_id,
        limit=int(limit),
        offset=int(offset),
    )

    if not messages:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Messages not found."
        )

    # TODO: change to schema
    return messages


@router.post("/message", status_code=HTTP_201_CREATED)
@handle_deal_errors
async def write_deal_message(
    message: MessageCreateSchema = Depends(),
    jwt: TokenPayload = Depends(auth_dependency),
    deal_service: AbstractDealService = Depends(deal_service_dependency),
):
    await deal_service.write_message(
        message=message, user_id=UUID(jwt.user_id)
    )
    return {"message": "Message written successfully"}


@router.patch("/change_sale_stage/{deal_id}")
@handle_deal_errors
async def change_sale_stage(
    deal_id: UUID,
    sale_stage_id: int = Body(ge=1, le=MAX_DB_INT, embed=True),
    deal_service: AbstractDealService = Depends(deal_service_dependency),
):
    updated_deals = await deal_service.change_sale_stage(
        deal_id=deal_id, sale_stage_id=sale_stage_id
    )

    if updated_deals:
        return {
            "status": "success",
            "detail": "The deal stage updated successfully!",
            "updated_quantity": updated_deals,
        }
    else:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Deal not found"
        )


@router.patch("/change_deal_fields/{deal_id}")
@handle_deal_errors
async def change_deal_fields(
    deal_id: UUID,
    fields: dict = Body(embed=True),
    deal_service: AbstractDealService = Depends(deal_service_dependency),
):
    updated_deals = await deal_service.change_fields(
        deal_id=deal_id, fields=fields
    )

    if updated_deals:
        return {
            "status": "success",
            "detail": "The deal fields updated successfully!",
            "updated_quantity": updated_deals,
        }
    else:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Deal not found"
        )


@router.patch("/close/{deal_id}")
async def close_deal(
    deal_id: UUID,
    lost: LostCreateSchema = Body(),
    deal_service: AbstractDealService = Depends(deal_service_dependency),
):
    try:
        deals_closed = await deal_service.close_deal(deal_id, lost)
        if deals_closed:
            return {
                "status": "success",
                "detail": "The deal closed successfully!",
                "closed_quantity": deals_closed,
            }
        else:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Deal with id {deal_id} doesn't exists",
            )

    except (
        DealLeadNotFoundError,
        DealManagerNotFoundError,
        DealSaleStageNotFoundError,
        DealLostReasonNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except DealAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except (DealError, DealDBError) as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.put("/{deal_id}")
async def update_deal(
    deal_id: UUID,
    deal_update: DealUpdateSchema = Body(),
    deal_service: AbstractDealService = Depends(deal_service_dependency),
):
    try:
        deal = await deal_service.update(
            deal_id=deal_id, deal_update_schema=deal_update
        )

        deal_response = get_deal_response(deal)
        return deal_response

    except (
        DealLeadNotFoundError,
        DealManagerNotFoundError,
        DealSaleStageNotFoundError,
        DealLostReasonNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except DealAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except (DealError, DealDBError) as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get("/{deal_id}", response_model=MessageResponseSchema)
async def get_deal(
    deal_id: UUID,
    deal_service: AbstractDealService = Depends(deal_service_dependency),
):
    try:
        deal = await deal_service.get(
            deal_id=deal_id,
        )

        deal_response = get_deal_response(deal)
        return deal_response

    except (
        DealLeadNotFoundError,
        DealManagerNotFoundError,
        DealSaleStageNotFoundError,
        DealLostReasonNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except DealAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except (DealError, DealDBError) as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error
