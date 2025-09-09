from datetime import UTC, datetime, timedelta
from uuid import UUID

from pydantic import BaseModel, Field

from core.general_constants import BASE_MIN_STR_LENGTH, MAX_MESSAGE_LENGTH


class MessageCreateDTO(BaseModel):
    deal_id: UUID
    message: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=MAX_MESSAGE_LENGTH,
    )
    user_id: UUID
    sent_at: datetime = Field(default=datetime.now(tz=UTC))
