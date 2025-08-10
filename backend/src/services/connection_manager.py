from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi import WebSocket

from core.logger.logger import get_configure_logger
from domain.exceptions import ChatNotActiveError

logger = get_configure_logger(Path(__file__).stem)


class WebSocketManager:
    def __init__(self):
        # Хранение активных соединений в виде {room_id: {user_id: WebSocket}}
        self.active_connections: dict[UUID, dict[UUID, WebSocket]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        room_id: UUID,
        user_id: UUID,
    ):
        """
        Устанавливает соединение с пользователем.
        websocket.accept() — подтверждает подключение.
        """
        await websocket.accept()
        if room_id not in self.active_connections:
            logger.debug(
                "New room registered in the websocket channels: %s",
                room_id,
            )
            self.active_connections[room_id] = {}
        self.active_connections[room_id][user_id] = websocket

    def disconnect(
        self,
        room_id: UUID,
        user_id: UUID,
    ):
        """
        Закрывает соединение и удаляет его из списка активных подключений.
        Если в комнате больше нет пользователей, удаляет комнату.
        """
        if (
            room_id in self.active_connections
            and user_id in self.active_connections[room_id]
        ):
            del self.active_connections[room_id][user_id]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(
        self,
        message: str,
        room_id: UUID,
        sender_id: UUID,
    ):
        """
        Рассылает сообщение всем пользователям в комнате.
        """
        room_id = room_id
        sender_id = sender_id
        if room_id in self.active_connections:
            for user_id, connection in self.active_connections[
                room_id
            ].items():
                logger.debug(
                    "Message received from user %s in the %s room",
                    user_id,
                    room_id,
                )
                message_with_class = {
                    "text": message,
                    "is_self": user_id == sender_id,
                    "sent_at": str(datetime.now(tz=UTC)),
                }
                await connection.send_json(message_with_class)
        else:
            raise ChatNotActiveError(
                f"Chat with id {room_id} does not active."
            )


# create the instance
websocket_manager = WebSocketManager()


def websocket_maganer_dependency() -> WebSocketManager:
    return websocket_manager
