from datetime import UTC, datetime, timedelta
from uuid import UUID

from pydantic import BaseModel, Field

from core.general_constants import BASE_MIN_STR_LENGTH, MAX_MESSAGE_LENGTH


class MessageResponseSchema(BaseModel):
    message_id: int
    deal_id: UUID
    message: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=MAX_MESSAGE_LENGTH,
    )
    user_id: UUID
    sent_at: datetime = Field(le=datetime.now(tz=UTC) + timedelta(seconds=5))
