from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi import Depends
from sqlalchemy import text, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import crm_settings
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
from dto.deal_dto import DealCreateDTO, DealUpdateDTO, LostReasonDTO
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

    @staticmethod
    def delete_old_deal_versions(function):
        async def inner(self, deal_id: UUID, *args, **kwargs):
            try:
                async with self.__session as session:
                    await session.execute(
                        text(
                            """
                            with deleted_deal as (
                                select deal_history_id
                                from deal_history
                                where deal_id = :deal_id
                                order by changed_at desc
                                offset :max_deal_saves
                            )
                            delete from deal_history
                            where deal_history_id in
                                (select deal_history_id from deleted_deal);
                            """
                        ),
                        params={
                            "deal_id": deal_id,
                            "max_deal_saves": crm_settings.max_deal_saves - 1,
                        },
                    )
                    await session.commit()
            except Exception as e:
                logger.error(e)

            return await function(self, deal_id, *args, **kwargs)

        return inner

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

    async def update(self, deal_id: UUID, deal_update: DealUpdateDTO): ...

    @delete_old_deal_versions
    async def close_deal(
        self, deal_id: UUID, lost: LostReasonDTO | None = None
    ) -> int:
        stmt = (
            update(DealModel)
            .where(DealModel.deal_id == deal_id)
            .values(close_at=datetime.now(tz=UTC))
        )

        if lost:
            stmt = stmt.values(
                lost_reason_id=lost.lost_reason_id,
                lost_reason_additional_text=lost.description,
            )

        try:
            async with self.__session as session:
                result = await session.execute(stmt)
                await session.commit()

            return result.rowcount

        except IntegrityError as error:
            self._validate_integrity_errors(error)
        except DBAPIError as error:
            logger.error(
                "DBAPIError when update a deal with id %s",
                deal_id,
                exc_info=error,
            )
            raise DealDBError from error


def deal_repository_dependency(
    async_session: AsyncSession = Depends(postgres_helper.session_dependency),
) -> AbstractDealRepository:
    return DealRepository(session=async_session)
