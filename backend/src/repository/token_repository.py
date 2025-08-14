from datetime import UTC, datetime
from functools import wraps
from pathlib import Path
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, func, update
from sqlalchemy.exc import DatabaseError, DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import RefreshToken
from domain.exceptions import (
    RefreshTokenAbsenceError,
    TokenDatabaseError,
    UserDoesNotExistsError,
)
from repository.abc.token_repository_abc import TokenRepositoryABC
from services.classes.token import RefreshTokenPayload

logger = get_configure_logger(Path(__file__).stem)


class TokenRepository(TokenRepositoryABC):
    """Manages database operations related to refresh tokens.

    Provides methods to check token status, clear expired tokens, and
    insert new tokens.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the TokenRepository with an asynchronous database session.

        Args:
            session: The SQLAlchemy asynchronous session for database ops.
        """
        self.__session = session

    async def is_token_in_black_list(self, token_id: UUID) -> bool:
        """Check if a specific refresh token is blocked (blacklisted).

        Args:
            token_id: The UUID of the refresh token to check.

        Returns:
            True if the token is blocked, False otherwise.

        Raises:
            RefreshTokenAbsenceError: If the token is not found.
            TokenDatabaseError: For any database operation failures.
        """
        from sqlalchemy import select

        stmt = select(RefreshToken.is_blocked).where(
            RefreshToken.refresh_token_id == token_id
        )
        try:
            result = await self.__session.execute(stmt)
            is_blocked = result.scalar_one_or_none()

            if is_blocked is None:
                raise RefreshTokenAbsenceError

            return is_blocked

        except DatabaseError as error:
            raise TokenDatabaseError from error

    @staticmethod
    def clear_expires_tokens(function):
        """Clear expired refresh tokens from the database. (decorator)

        This decorator executes before the decorated function, deleting
        any refresh tokens whose `expire_at` timestamp is in the past.
        It commits the changes to the database.

        Args:
            func: The function to be wrapped.

        Returns:
            The wrapper function.

        Raises:
            TokenDatabaseError: If a database error occurs during clearing.
        """

        @wraps(function)
        async def wrapper(self, *args, **kwargs):
            try:
                clear_stmt = delete(RefreshToken).where(
                    RefreshToken.expire_at >= func.current_timestamp()
                )

                await self.__session.execute(clear_stmt)
                await self.__session.commit()

            except DatabaseError as error:
                logger.error(
                    "Database error while clearing expired tokens",
                    exc_info=error,
                )
                raise TokenDatabaseError from error

            return await function(self, *args, **kwargs)

        return wrapper

    async def close_session(self, token_id: UUID) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.refresh_token_id == token_id)
            .values(is_blocked=True)
        )

        try:
            await self.__session.execute(stmt)
            await self.__session.commit()
        except DatabaseError as error:
            logger.error(
                "Database error while closing session",
                exc_info=error,
            )
            raise TokenDatabaseError from error

    @clear_expires_tokens
    async def insert_refresh_token(
        self,
        token: RefreshTokenPayload,
    ):
        """Insert a new refresh token record into the database.

        Args:
            token: The RefreshTokenPayload object containing token details.

        Raises:
            TokenDatabaseError: If a database error occurs during insertion.
        """
        refresh_token = RefreshToken(
            refresh_token_id=token.token_id,
            user_id=token.user_id,
            fingerprint=token.fingerprint,
            ip=token.ip,
            expire_at=datetime.fromtimestamp(token.exp, tz=UTC),
        )

        try:
            self.__session.add(refresh_token)
            await self.__session.commit()
        except IntegrityError as error:
            if "refresh_token_user_id_fkey" in str(error):
                raise UserDoesNotExistsError from error
            logger.error(
                "Unexpected database error while inserting refresh token",
                exc_info=error,
            )
            raise TokenDatabaseError from error
        except DBAPIError as error:
            logger.error(
                "Unexpected database error while inserting refresh token",
                exc_info=error,
            )
            raise TokenDatabaseError from error


def token_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return TokenRepository(session=session)
