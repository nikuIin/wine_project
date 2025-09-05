from pydantic import BaseModel


class PartnerBaseDTO(BaseModel):
    name: str
    image_src: str | None


class PartnerDTO(PartnerBaseDTO):
    partner_id: int


class PartnerCreateDTO(PartnerBaseDTO):
    pass


class PartnerUpdateDTO(PartnerBaseDTO): ...
