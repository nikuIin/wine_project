from abc import ABC, abstractmethod
from uuid import UUID

from core.general_constants import DEFAULT_LIMIT
from domain.entities.deal import Deal
from dto.deal_dto import DealCreateDTO, DealUpdateDTO, LostReasonDTO


class AbstractDealRepository(ABC):
    """Repository layer, those works with deals in the CRM system."""

    @abstractmethod
    async def create(self, deal_create: DealCreateDTO):
        raise NotImplementedError

    @abstractmethod
    async def close_deal(
        self, deal_id: UUID, lost: LostReasonDTO | None = None
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, deal_id: UUID, deal_update: DealUpdateDTO
    ) -> Deal | None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, deal_id: UUID) -> Deal | None:
        raise NotImplementedError

    @abstractmethod
    async def change_sale_stage(
        self,
        deal_id: UUID,
        sale_stage_id: int,
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
        `fields` column in the database for the specified deal.

        Args:
            deal_id: The unique identifier of the deal to update.
            fields: A dictionary of fields to merge into the deal's existing
                    `fields`.

        Returns:
            The number of rows updated.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_deals(
        self,
        limit: int,
        offset: int,
    ) -> list[Deal]:
        raise NotImplementedError

    # @abstractmethod
    # async def get_messages(self):
    #     raise NotImplementedError

    # @abstractmethod
    # async def write_message(self):
    #     raise NotImplementedError
