from pathlib import Path
from uuid import UUID

from fastapi import Depends, WebSocket
from uuid_extensions import uuid7

from core.general_constants import DEFAULT_LIMIT
from core.logger.logger import get_configure_logger
from domain.entities.deal import Deal
from domain.entities.message import Message
from domain.exceptions import ManagersDoesNotExistsError
from dto.deal_dto import (
    DealCreateDTO,
    DealShortDTO,
    DealUpdateDTO,
    LostReasonDTO,
    ManagerOpenDealsDTO,
)
from dto.message_dto import MessageCreateDTO
from repository.abc.deal_repository_abc import AbstractDealRepository
from repository.deal_repository import deal_repository_dependency
from schemas.deal_schema import (
    DealCreateSchema,
    DealUpdateSchema,
    LostCreateSchema,
)
from schemas.message_schema import MessageCreateSchema
from services.abc.deal_service_abc import AbstractDealService
from services.connection_manager import (
    WebSocketManager,
    websocket_maganer_dependency,
)

logger = get_configure_logger(Path(__file__).stem)


class DealService(AbstractDealService):
    def __init__(
        self,
        deal_repository: AbstractDealRepository,
        websocket_manager: WebSocketManager,
    ):
        self.__deal_repository = deal_repository
        self.__websocket_manager = websocket_manager

    async def select_manager_to_deal(self) -> UUID:
        managers = await self.__deal_repository.get_managers_with_quantity_of_open_deals()
        if not managers:
            logger.error("There are no managers in the system")
            raise ManagersDoesNotExistsError("There are no managers")

        return min(
            managers, key=lambda manager: manager.open_deals_count
        ).manager_id

    async def create(self, deal_create_schema: DealCreateSchema) -> UUID:
        # Data preparation
        deal_id = uuid7()
        manager_id = (
            await self.select_manager_to_deal()
            if not deal_create_schema.manager_id
            else deal_create_schema.manager_id
        )

        await self.__deal_repository.create(
            deal_create=DealCreateDTO(
                **deal_create_schema.model_dump(),
                manager_id=manager_id,
                deal_id=deal_id,
            )
        )

        return deal_id

    async def close_deal(
        self, deal_id: UUID, lost: LostCreateSchema | None = None
    ) -> int:
        return await self.__deal_repository.close_deal(
            deal_id=deal_id,
            lost=LostReasonDTO(**lost.model_dump(exclude_unset=True))
            if lost
            else None,
        )

    async def update(
        self, deal_id: UUID, deal_update_schema: DealUpdateSchema
    ) -> Deal | None:
        return await self.__deal_repository.update(
            deal_id=deal_id,
            deal_update=DealUpdateDTO(**deal_update_schema.model_dump()),
        )

    async def get(self, deal_id: UUID) -> Deal | None:
        return await self.__deal_repository.get(
            deal_id=deal_id,
        )

    async def change_sale_stage(
        self,
        deal_id: UUID,
        sale_stage_id: int,
    ) -> int:
        return await self.__deal_repository.change_sale_stage(
            deal_id=deal_id, sale_stage_id=sale_stage_id
        )

    async def change_fields(
        self,
        deal_id: UUID,
        fields: dict,
    ) -> int:
        return await self.__deal_repository.change_fields(
            deal_id=deal_id, fields=fields
        )

    async def get_deals(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> list[DealShortDTO]:
        return await self.__deal_repository.get_deals(
            limit=limit,
            offset=offset,
        )

    async def get_messages(
        self,
        deal_id: UUID,
        limit: int,
        offset: int,
    ) -> list[Message]:
        return await self.__deal_repository.get_messages(
            deal_id,
            limit,
            offset,
        )

    async def connect_to_chat(
        self, websocket: WebSocket, deal_id: UUID, user_id: UUID
    ):
        await self.__websocket_manager.connect(
            websocket=websocket, room_id=deal_id, user_id=user_id
        )

    def disconnect(self, deal_id: UUID, user_id: UUID):
        self.__websocket_manager.disconnect(
            room_id=deal_id,
            user_id=user_id,
        )

    async def write_message(
        self,
        user_id: UUID,
        message: MessageCreateSchema,
    ):
        # TODO: check is user hass access to the deal.
        # (the user_role must be higher or equal than manager
        # or user_id=lead_id)
        await self.__websocket_manager.broadcast(
            message=message.message,
            room_id=message.deal_id,
            sender_id=user_id,
        )
        await self.__deal_repository.write_message(
            message_data=MessageCreateDTO(
                **message.model_dump(),
                user_id=user_id,
            )
        )


def deal_service_dependency(
    deal_repository: AbstractDealRepository = Depends(
        deal_repository_dependency
    ),
    websocket_manager: WebSocketManager = Depends(
        websocket_maganer_dependency
    ),
) -> AbstractDealService:
    return DealService(
        deal_repository=deal_repository,
        websocket_manager=websocket_manager,
    )
