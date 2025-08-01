from abc import ABC, abstractmethod


class AbstractDealService(ABC):
    @abstractmethod
    async def create(self, deal_create_schema: ...):
        raise NotImplementedError
