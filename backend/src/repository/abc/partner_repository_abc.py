from abc import ABC, abstractmethod

from dto.partner_dto import PartnerCreateDTO, PartnerDTO, PartnerUpdateDTO


class AbstractPartnerRepository(ABC):
    @abstractmethod
    async def get_partner(self, partner_id: int) -> PartnerDTO | None:
        pass

    @abstractmethod
    async def create_partner(
        self, partner_data: PartnerCreateDTO
    ) -> PartnerDTO:
        pass

    @abstractmethod
    async def update_partner(
        self, partner_id: int, partner_data: PartnerUpdateDTO
    ) -> PartnerDTO | None:
        pass

    @abstractmethod
    async def delete_partner(self, partner_id: int) -> bool:
        pass
