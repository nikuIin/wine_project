from pydantic import BaseModel, Field

from core.general_constants import DEFAULT_LIMIT, MAX_LIMIT


class OffsetSchema(BaseModel):
    offset: int = Field(default=0, ge=0)

    def __int__(self):
        return self.offset


class LimitSchema(BaseModel):
    limit: int = Field(
        default=DEFAULT_LIMIT,
        ge=1,
        le=MAX_LIMIT,
    )

    def __int__(self):
        return self.limit


class OrderSchema(BaseModel):
    # TODO: добавить enum на разные типы сортировки
    ...
