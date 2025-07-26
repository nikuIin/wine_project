from pathlib import Path
from uuid import UUID

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from domain.entities.user import USER_ROLE_ID, UserBase, UserCreate, UserCreds
from domain.exceptions import (
    EmailDBError,
    UserAlreadyExistsError,
    UserDBError,
    UserDoesNotExistsError,
    UserIntegrityError,
)
from repository.sql_queries.user_queries import GET_USER_CREDS

logger = get_configure_logger(Path(__file__).stem)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_user_creds(self, login: str) -> UserCreds | None:
        async with self.__session as session:
            result = await session.execute(
                GET_USER_CREDS, params={"login": login}
            )
        result = result.mappings().fetchone()

        return UserCreds(**result) if result else None

    async def create_user(self, user: UserCreate) -> UserBase:
        insert_user_data = text(
            """
            insert into
            "user"(
                user_id,
                login,
                password,
                email,
                role_id,
                created_at,
                is_registered
            )
            values(
                :user_id,
                :login,
                :password,
                :email,
                :role_id,
                current_timestamp,
                false
            )
            """
        )
        insert_md_data_stmt = text(
            """
            insert into md_user (user_id)
            values (:user_id)
            """
        )
        try:
            async with self.__session as session:
                await session.execute(
                    insert_user_data,
                    params={
                        "user_id": user.user_id,
                        "login": user.login,
                        "email": user.email,
                        "password": user.password,
                        "role_id": USER_ROLE_ID,
                    },
                )
                await session.execute(
                    insert_md_data_stmt,
                    params={
                        "user_id": user.user_id,
                    },
                )
                await session.commit()

            return UserBase(**user.model_dump())
        # === errors handling ===
        except IntegrityError as error:
            logger.debug(
                "IntegrityError while adding user with id %s",
                user.user_id,
                exc_info=error,
            )

            if isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore  # noqa: SIM102
                if "md_user_pkey" in str(error):
                    raise UserDoesNotExistsError(
                        f"User with id {user.user_id} does't exists."
                    ) from error
            elif isinstance(error.orig.__cause__, UniqueViolationError):  # type: ignore  # noqa: SIM102
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
        stmt = text('select email from "user" where user_id = :user_id')

        try:
            # === main logic ===
            async with self.__session as session:
                result = await session.execute(
                    stmt,
                    params={"user_id": user_id},
                )

            return result.scalar_one_or_none()

        # === errors handling ===
        except IntegrityError as error:
            logger.debug(
                "IntegrityError while get email of user with id %s",
                user_id,
                exc_info=error,
            )

            if isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore  # noqa: SIM102
                if "md_user_pkey" in str(error):
                    raise UserDoesNotExistsError(
                        f"User with id {user_id} does't exists."
                    ) from error

            raise UserIntegrityError(
                f"Integrity error of getting email of user with id {user_id}"
            ) from error

        except DBAPIError as error:
            logger.error(
                "DBError while getting email of user with id %s",
                user_id,
                exc_info=error,
            )
            raise UserDBError(
                f"DBError of getting email of user with id {user_id}"
            ) from error

    async def is_user_exists(self, email: EmailStr, login: str) -> bool:
        stmt = text(
            """
            select true
            from md_user
            join "user" using(user_id)
            where email = :email
                  or login = :login
            limit 1;
            """
        )

        try:
            async with self.__session as session:
                result = await session.execute(
                    stmt,
                    params={
                        "email": email,
                        "login": login,
                    },
                )

            result = result.scalar_one_or_none()
            logger.debug(
                "Is user with data (%s, %s) exists: %s", email, login, result
            )
            return bool(result)

        except DBAPIError as error:
            logger.error(
                "DBError while search mail from md_user table", exc_info=error
            )
            raise EmailDBError from error

    async def register_user(self, user_id: UUID):
        """Set is_register in the user table to True"""

        stmt = text(
            """
            update "user" set is_registered = True where user_id = :user_id
            """
        )

        try:
            async with self.__session as session:
                result = await session.execute(
                    stmt, params={"user_id": user_id}
                )
                await session.commit()

            update_rows_quantity = result.rowcount  # type: ignore

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
):
    return UserRepository(session=session)
