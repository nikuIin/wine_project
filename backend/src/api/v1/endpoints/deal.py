from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from domain.exceptions import (
    DealAlreadyExistsError,
    DealDBError,
    DealError,
    DealLeadNotFoundError,
    DealLostReasonNotFoundError,
    DealManagerNotFoundError,
    DealSaleStageNotFoundError,
)
from schemas.deal_schema import DealCreateSchema, LostBaseSchema
from services.abc.deal_service_abc import AbstractDealService
from services.deal_service import deal_service_dependency

router = APIRouter(prefix="/deal", tags=["deal"])


@router.post("/")
async def create_deal(
    deal_create_data: DealCreateSchema = Body(),
    deal_service: AbstractDealService = Depends(deal_service_dependency),
):
    try:
        await deal_service.create(deal_create_data)
        return {
            "status": "success",
            "detail": "The deal create successfully!",
        }

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


@router.patch("/{deal_id}")
async def close_deal(
    deal_id: UUID,
    lost: LostBaseSchema = Body(),
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
