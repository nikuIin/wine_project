from pathlib import Path

from fastapi import Depends
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import Deal as DealModel
from domain.exceptions import (
    DealAlreadyExistsError,
    DealDBError,
    DealError,
    DealLeadNotFoundError,
    DealLostReasonNotFoundError,
    DealManagerNotFoundError,
    DealSaleStageNotFoundError,
)
from dto.deal_dto import DealCreateDTO
from repository.abc.deal_repository_abc import AbstractDealRepository

logger = get_configure_logger(Path(__file__).stem)


class DealRepository(AbstractDealRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session

    def _validate_integrity_errors(self, error: IntegrityError):
        logger.debug("Integrity error of deal operation", exc_info=error)
        if "deal_lead_id_fkey" in str(error):
            raise DealLeadNotFoundError from error
        elif "deal_pkey" in str(error) or "deal_lead_id_key" in str(error):
            raise DealAlreadyExistsError from error
        elif "deal_manager_id_fkey" in str(error):
            raise DealManagerNotFoundError from error
        elif "deal_sale_stage_id_fkey" in str(error):
            raise DealSaleStageNotFoundError from error
        elif "deal_lost_reason_id_fkey" in str(error):
            raise DealLostReasonNotFoundError from error

        logger.error(
            "Undefined IntegrityError when create deal",
            exc_info=error,
        )
        raise DealError from error

    async def create(self, deal_create: DealCreateDTO):
        deal_model = DealModel(**deal_create.model_dump())

        try:
            async with self.__session as session:
                session.add(deal_model)
                await session.commit()

        except IntegrityError as error:
            self._validate_integrity_errors(error)

        except DBAPIError as error:
            logger.error(
                "DBAPIError when create a deal",
                exc_info=error,
            )
            raise DealDBError from error


def deal_repository_dependency(
    async_session: AsyncSession = Depends(postgres_helper.session_dependency),
) -> AbstractDealRepository:
    return DealRepository(session=async_session)
