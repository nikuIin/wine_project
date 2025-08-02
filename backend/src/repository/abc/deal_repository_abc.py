from abc import ABC, abstractmethod
from uuid import UUID

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

    # @abstractmethod
    # async def get_info(self, deal_id: UUID) -> Deal:
    #     raise NotImplementedError

    # @abstractmethod
    # async def change_sale_stage(
    #     self,
    #     deal_id: UUID,
    #     sale_stage: int,
    # ) -> None:
    #     raise NotImplementedError

    # @abstractmethod
    # async def get_messages(self):
    #     raise NotImplementedError

    # @abstractmethod
    # async def write_message(self):
    #     raise NotImplementedError

    # @abstractmethod
    # async def insert_new_field(self):
    #     raise NotImplementedError
