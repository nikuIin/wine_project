from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, text, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import crm_settings
from core.general_constants import DEFAULT_LIMIT
from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import Deal as DealModel
from db.models import DealMessage, LostReason
from db.models import MdUser as MdUserModel
from domain.entities.deal import Deal
from domain.entities.message import Message
from domain.exceptions import (
    DealAlreadyExistsError,
    DealDBError,
    DealError,
    DealLeadNotFoundError,
    DealLostReasonNotFoundError,
    DealManagerNotFoundError,
    DealSaleStageNotFoundError,
)
from dto.deal_dto import (
    DealCreateDTO,
    DealShortDTO,
    DealUpdateDTO,
    LostReasonDTO,
)
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

    @delete_old_deal_versions
    async def update(
        self, deal_id: UUID, deal_update: DealUpdateDTO
    ) -> Deal | None:
        update_stmt = (
            update(DealModel)
            .where(DealModel.deal_id == deal_id)
            .values(
                sale_stage_id=deal_update.sale_stage_id,
                manager_id=deal_update.manager_id,
                fields=deal_update.fields,
                cost=deal_update.cost,
                probability=deal_update.probability,
                priority=deal_update.priority,
                close_at=deal_update.close_at,
            )
        )

        if deal_update.lost:
            update_stmt = update_stmt.values(
                lost_reason_id=deal_update.lost.lost_reason_id,
                lost_reason_additional_text=deal_update.lost.description,
            )
        else:
            update_stmt = update_stmt.values(
                lost_reason_id=None,
                lost_reason_additional_text=None,
            )

        update_cte = update_stmt.returning(DealModel).cte("updated_deal")

        select_stmt = select(
            update_cte, LostReason.name.label("lost_reason_name")
        ).outerjoin(
            LostReason,
            update_cte.c.lost_reason_id == LostReason.lost_reason_id,
        )

        try:
            async with self.__session as session:
                deal_row = await session.execute(select_stmt)
                deal_row = deal_row.mappings().one_or_none()
                await session.commit()

            if not deal_row:
                return None

            deal_data = dict(deal_row)
            deal_data["lost_reason"] = deal_row.lost_reason_name
            deal_data["lost_reason_description"] = (
                deal_row.lost_reason_additional_text
            )

            return Deal(
                **deal_data,
            )

        except IntegrityError as error:
            self._validate_integrity_errors(error)
        except DBAPIError as error:
            logger.error(
                "DBAPI error when update deal %s", deal_id, exc_info=error
            )
            raise DealDBError from error

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

    async def get(self, deal_id: UUID) -> Deal | None:
        select_stmt = (
            select(
                DealModel.deal_id,
                DealModel.sale_stage_id,
                DealModel.lead_id,
                DealModel.probability,
                DealModel.priority,
                DealModel.lost_reason_additional_text.label(
                    "lost_reason_description"
                ),
                DealModel.fields,
                DealModel.cost,
                DealModel.created_at,
                DealModel.close_at,
                DealModel.manager_id,
                LostReason.name.label("lost_reason"),
            )
            .where(DealModel.deal_id == deal_id)
            .outerjoin(
                LostReason,
                DealModel.lost_reason_id == LostReason.lost_reason_id,
            )
        )

        try:
            async with self.__session as session:
                deal_row = await session.execute(select_stmt)

            deal_row = deal_row.mappings().fetchone()

            deal = Deal.model_validate(deal_row) if deal_row else None
            return deal

        except IntegrityError as error:
            self._validate_integrity_errors(error)
        except DBAPIError as error:
            logger.error(
                "DBAPIError when get a deal with id %s",
                deal_id,
                exc_info=error,
            )
            raise DealDBError from error

    @delete_old_deal_versions
    async def change_sale_stage(
        self, deal_id: UUID, sale_stage_id: int
    ) -> int:
        stmt = (
            update(DealModel)
            .where(DealModel.deal_id == deal_id)
            .values(sale_stage_id=sale_stage_id)
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
                "DBAPIError when update sale sale stage in the %s deal."
                + " (To sale_stage_id=%s)",
                deal_id,
                sale_stage_id,
                exc_info=error,
            )
            raise DealDBError from error

    @delete_old_deal_versions
    async def change_fields(
        self,
        deal_id: UUID,
        fields: dict,
    ) -> int:
        """Update specific fields of an existing deal.

        This method merges the provided `fields` dictionary with the existing
        `fields` column in the database for the specified deal,
        using the PostgreSQL JSONB concatenation operator (||).

        Args:
            deal_id: The unique identifier of the deal to update.
            fields: A dictionary of fields to merge into the deal's existing
                    `fields` JSONB column.

        Returns:
            The number of rows updated (1 if deal exists, 0 otherwise).

        Raises:
            DealLeadNotFoundError: If the associated lead ID does not
                                   exist.
            DealAlreadyExistsError: If a deal with the same ID or
                                    lead ID exists.
            DealManagerNotFoundError: If the associated manager ID is
                                      not found.
            DealSaleStageNotFoundError: If the associated sale stage
                                        ID is not found.
            DealLostReasonNotFoundError: If the associated lost reason
                                         ID is not found.
            DealError: For other integrity errors not specifically handled.
            DealDBError: For general database API errors during the update.
        """

        stmt = (
            update(DealModel)
            .where(DealModel.deal_id == deal_id)
            .values(fields=DealModel.fields.op("||")(fields))
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
                "DBAPIError when update fields in the %s deal."
                + " (Fields: %s)",
                deal_id,
                fields,
                exc_info=error,
            )
            raise DealDBError from error

    async def get_deals(
        self, limit: int = DEFAULT_LIMIT, offset: int = 0
    ) -> list[DealShortDTO]:
        stmt = (
            select(
                DealModel.deal_id,
                DealModel.sale_stage_id,
                DealModel.lead_id,
                MdUserModel.first_name.label("lead_name"),
                MdUserModel.last_name.label("lead_last_name"),
                MdUserModel.profile_picture_link,
            )
            .outerjoin(MdUserModel, MdUserModel.user_id == DealModel.lead_id)
            .order_by(DealModel.updated_at)
            .limit(limit)
            .offset(offset)
        )

        try:
            async with self.__session as session:
                result = await session.execute(stmt)
                deals_rows = result.mappings().all()

            return [DealShortDTO.model_validate(row) for row in deals_rows]

        except IntegrityError as error:
            self._validate_integrity_errors(error)

        except DBAPIError as error:
            logger.error(
                "DBAPIError when getting deals",
                exc_info=error,
            )
            raise DealDBError from error

    async def get_messages(
        self,
        deal_id: UUID,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> list[Message]:
        stmt = (
            select(
                DealMessage.deal_message_id.label("message_id"),
                DealMessage.message,
                DealMessage.sent_at,
                DealMessage.user_id,
                DealMessage.deal_id,
            )
            .where(DealMessage.deal_id == deal_id)
            .limit(limit)
            .offset(offset)
        )

        try:
            async with self.__session as session:
                result = await session.execute(stmt)

            messages = [Message(**row) for row in result.mappings().all()]
            return messages

        except IntegrityError as error:
            self._validate_integrity_errors(error)
        except DBAPIError as error:
            logger.error(
                "DBAPIError when getting message of deal whith id %s",
                deal_id,
                exc_info=error,
            )
            raise DealDBError from error


def deal_repository_dependency(
    async_session: AsyncSession = Depends(postgres_helper.session_dependency),
) -> AbstractDealRepository:
    return DealRepository(session=async_session)
