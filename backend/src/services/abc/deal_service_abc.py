from abc import ABC, abstractmethod
from uuid import UUID

from schemas.deal_schema import LostBaseSchema


class AbstractDealService(ABC):
    @abstractmethod
    async def create(self, deal_create_schema: ...):
        raise NotImplementedError

    @abstractmethod
    async def close_deal(self, deal_id: UUID, lost: LostBaseSchema) -> int:
        raise NotImplementedError
