from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.deal import Deal
from domain.entities.message import Message
from dto.deal_dto import DealShortDTO
from schemas.deal_schema import (
    DealCreateSchema,
    DealUpdateSchema,
    LostCreateSchema,
)
from schemas.message_schema import MessageCreateSchema


class AbstractDealService(ABC):
    @abstractmethod
    async def create(self, deal_create_schema: DealCreateSchema) -> UUID:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, deal_id: UUID, deal_update_schema: DealUpdateSchema
    ) -> Deal | None:
        raise NotImplementedError

    @abstractmethod
    async def get(
        self,
        deal_id: UUID,
    ) -> Deal | None:
        raise NotImplementedError

    @abstractmethod
    async def close_deal(self, deal_id: UUID, lost: LostCreateSchema) -> int:
        raise NotImplementedError

    @abstractmethod
    async def change_sale_stage(
        self, deal_id: UUID, sale_stage_id: int
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def change_fields(
        self,
        deal_id: UUID,
        fields: dict,
    ) -> int:
        """Update specific fields of an existing deal.

        This method merges the provided `fields` dictionary with the existing
        fields of the specified deal.

        Args:
            deal_id: The unique identifier of the deal to update.
            fields: A dictionary of fields to merge into the deal's existing
                    fields.

        Returns:
            The number of affected entities (typically 1 if the deal exists).
        """
        raise NotImplementedError

    @abstractmethod
    async def get_deals(
        self,
        limit: int,
        offset: int,
    ) -> list[DealShortDTO]:
        raise NotImplementedError

    @abstractmethod
    async def get_messages(
        self,
        deal_id: UUID,
        limit: int,
        offset: int,
    ) -> list[Message]:
        raise NotImplementedError

    @abstractmethod
    async def write_message(
        self,
        user_id: UUID,
        message: MessageCreateSchema,
    ):
        raise NotImplementedError
