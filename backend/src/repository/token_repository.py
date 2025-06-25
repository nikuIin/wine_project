from datetime import datetime
from pathlib import Path
from uuid import UUID

from fastapi import Depends
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from domain.entities.token import RefreshTokenPayload
from domain.exceptions import RefreshTokenCreationError
from repository.sql_queries.token_queries import (
    CREATE_OR_UPDATE_REFRESH_TOKEN,
    IS_TOKEN_IN_BLACK_LIST,
)

logger = get_configure_logger(Path(__file__).stem)


class TokenRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def is_token_in_black_list(self, token_id: UUID) -> bool:
        async with self.__session as session:
            result = await session.execute(
                IS_TOKEN_IN_BLACK_LIST,
                params={"refresh_token_id": token_id},
            )

        result = result.mappings().fetchone()
        if result:
            return result["is_in_black_list"] is True
        return False

    async def create_or_update_refresh_token(
        self, token: RefreshTokenPayload, expire_date: datetime
    ) -> RefreshTokenPayload:
        try:
            async with self.__session as session:
                await session.execute(
                    CREATE_OR_UPDATE_REFRESH_TOKEN,
                    params={
                        "refresh_token_id": UUID(token.token_id),
                        "user_id": token.user_id,
                        "expire_at": expire_date,
                    },
                )
                await session.commit()
        except DatabaseError as error:
            logger.error(
                "Error when creating or updating JWT token with id %s",
                token.token_id,
                exc_info=error,
            )
            raise RefreshTokenCreationError from error
        return token


def token_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return TokenRepository(session=session)
