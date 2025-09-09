from abc import ABC, abstractmethod

from core.general_constants import DEFAULT_LIMIT
from dto.partner_dto import PartnerDTO


class AbstractPartnerService(ABC):
    @abstractmethod
    async def get_partners(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> list[PartnerDTO]:
        pass
