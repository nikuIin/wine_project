from pathlib import Path
from uuid import UUID

from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy import insert, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.general_constants import USER_ROLE
from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import MdUser, User
from domain.exceptions import (
    EmailDBError,
    UserAlreadyExistsError,
    UserDBError,
    UserDoesNotExistsError,
    UserIntegrityError,
)
from dto.user_dto import UserBase, UserCreate, UserCreds
from repository.abc.user_repository_abc import UserRepositoryABC

logger = get_configure_logger(Path(__file__).stem)


class UserRepository(UserRepositoryABC):
    """
    Manage user-related database operations.

    This repository handles interactions with the `User` and `MdUser` models,
    providing methods for user creation, retrieval, and updates.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the user repository with an asynchronous database session.

        Args:
            session: The SQLAlchemy asynchronous session.
        """
        self.__session = session

    async def get_user_creds(self, login: str) -> UserCreds | None:
        """
        Retrieve user credentials by login.

        Args:
            login: The user's login string.

        Returns:
            UserCreds: A DTO containing user ID, login, password, and role ID
                if found, otherwise None.
        """
        stmt = select(
            User.user_id,
            User.login,
            User.password,
            User.role_id,
        ).where(User.login == login)

        async with self.__session as session:
            result = await session.execute(stmt)
        result = result.mappings().fetchone()

        return UserCreds(**result) if result else None

    async def create_user(self, user: UserCreate) -> UserBase:
        """
        Create a new user and associated metadata in the database.

        Atomically inserts records into both the `user` and `md_user` tables.

        Args:
            user: A UserCreate DTO containing user details.

        Returns:
            UserBase: A DTO representing the newly created user.

        Raises:
            UserAlreadyExistsError: If a user with the given ID already exists.
            UserDoesNotExistsError: If a foreign key constraint issue occurs
                during `md_user` insertion, implying the user doesn't exist.
            UserIntegrityError: For other integrity constraint violations.
            UserDBError: For general database operational errors.
        """
        insert_user_stmt = insert(User).values(
            user_id=user.user_id,
            login=user.login,
            password=user.password,
            email=user.email,
            role_id=USER_ROLE,
        )
        insert_md_data_stmt = insert(MdUser).values(
            user_id=user.user_id,
        )

        try:
            async with self.__session as session:
                await session.execute(insert_user_stmt)
                await session.execute(insert_md_data_stmt)
                await session.commit()

            return UserBase(**user.model_dump())
        # === errors handling ===
        except IntegrityError as error:
            logger.debug(
                "IntegrityError while adding user with id %s",
                user.user_id,
                exc_info=error,
            )

            if "md_user_pkey" in str(error):
                raise UserDoesNotExistsError(
                    f"User with id {user.user_id} does't exists."
                ) from error
            if "user_pkey" in str(error):
                raise UserAlreadyExistsError(
                    f"User with id {user.user_id} already exists"
                ) from error

            raise UserIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DBError while adding user with id %s",
                user.user_id,
                exc_info=error,
            )
            raise UserDBError from error

    async def get_user_email(self, user_id: UUID) -> EmailStr | None:
        """
        Retrieve a user's email address by user ID.

        Args:
            user_id: The UUID of the user.

        Returns:
            EmailStr: The user's email address if found, otherwise None.
        """
        stmt = select(User.email).where(User.user_id == user_id)

        async with self.__session as session:
            result = await session.scalar(stmt)

        return result

    async def is_user_exists(self, email: EmailStr, login: str) -> bool:
        """
        Check if a user exists based on email or login.

        Args:
            email: The user's email address.
            login: The user's login string.

        Returns:
            bool: True if a user with the given email or login exists,
                False otherwise.

        Raises:
            EmailDBError: For database operational errors during the check.
        """
        stmt = (
            select(User.user_id)
            .where((User.email == email) | (User.login == login))
            .limit(1)
        )

        try:
            async with self.__session as session:
                result = await session.execute(stmt)

            result = result.scalar_one_or_none()
            logger.debug(
                "Is user with data (%s, %s) exists: %s",
                email,
                login,
                result is not None,
            )
            return result is not None

        except DBAPIError as error:
            logger.error(
                "DBError while search mail from md_user table", exc_info=error
            )
            raise EmailDBError from error

    async def register_user(self, user_id: UUID) -> int:
        """
        Set `is_registered` to True for a specific user.

        Updates the `is_registered` field in the `user` table to `True` for
        the given user ID.

        Args:
            user_id: The UUID of the user to register.

        Returns:
            int: The number of rows updated (0 or 1).

        Raises:
            UserIntegrityError: For integrity constraint violations during
                the update.
            UserDBError: For general database operational errors.
        """

        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(is_registered=True)
        )

        try:
            async with self.__session as session:
                result = await session.execute(stmt)
                await session.commit()

            update_rows_quantity = result.rowcount

            return update_rows_quantity

        # === errors handling ===
        except IntegrityError as error:
            logger.error(
                "IntegrityError while register user with id %s",
                user_id,
                exc_info=error,
            )
            raise UserIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DBError while adding user with id %s",
                user_id,
                exc_info=error,
            )
            raise UserDBError from error


def user_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
) -> UserRepository:
    """
    Provide a dependency for `UserRepository`.

    This function sets up `UserRepository` with an asynchronous database
    session for dependency injection.

    Args:
        session: An `AsyncSession` provided by `postgres_helper.session_dependency`.

    Returns:
        UserRepository: An instance of `UserRepository`.
    """
    return UserRepository(session=session)
