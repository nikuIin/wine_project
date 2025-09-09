from pathlib import Path
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.exc import DBAPIError
from uuid_extensions import uuid7

from core.logger.logger import get_configure_logger
from domain.exceptions import (
    EmailDBError,
    UserAlreadyExistsError,
    UserDBError,
    UserDoesNotExistsError,
    UserIntegrityError,
    ValidateVerificationKeyError,
)
from dto.user_dto import UserBase, UserCreate, UserCreds
from repository.user_repository import UserRepository
from services.abc.user_service_abc import AbstractUserService
from services.email_verification_service import EmailVerificationService

logger = get_configure_logger(Path(__file__).stem)


class UserService(AbstractUserService):
    def __init__(
        self,
        user_repository: UserRepository,
        email_verification_service: EmailVerificationService,
    ):
        self.__user_repository = user_repository
        self._email_verification_service = email_verification_service

    async def get_user_creds(
        self, login: str | None, email: str | None
    ) -> UserCreds | None:
        if not email and not login:
            raise ValueError("Either email or login must be provided")
        return await self.__user_repository.get_user_creds(
            login=login,
            email=email,
        )

    async def is_user_exists(self, email: EmailStr, login: str) -> bool:
        try:
            return await self.__user_repository.is_user_exists(
                email=email,
                login=login,
            )
        except (DBAPIError, UserIntegrityError) as error:
            raise error

    async def create_user_light(
        self,
    ) -> UUID:
        """Create a lightweight user with the given UUID.

        This method is used to remember user actions and is available after
        completing user registration to view all data saved before full
        registration.

        Args:
            user_id: The UUID to associate with the new user.

        Returns:
            The UUID of the created user.

        Raises:
            UserDBError: If there is an error creating the lightweight user in
                the database.
            UserAlreadyExists: If the user with this UUID already exists.
            UserIntegrityError: If there is a data integrity violation during
                creation.
        """
        try:
            user_id = uuid7()
            await self.__user_repository.create_user_light(user_id)
            return user_id
        except (UserDBError, UserIntegrityError) as error:
            logger.error(f"Failed to create lightweight user: {error}")
            raise

    async def create_user(self, user: UserCreate) -> UserBase:
        try:
            # === main logic ===
            # check is email exists
            if await self.is_user_exists(
                login=user.login,
                email=user.email,
            ):
                # if email already exists, we can't create the user
                raise UserAlreadyExistsError(
                    "User with this data already exists."
                )

            return await self.__user_repository.create_user(user=user)

        # === errors handling ===
        except UserDoesNotExistsError as error:
            raise error
        except UserAlreadyExistsError as error:
            raise error
        except UserIntegrityError as error:
            raise error
        except UserDBError as error:
            raise error

    async def register_user(self, user_id: UUID, validate_code: str) -> bool:
        try:
            if await self._email_verification_service.validate_verification_code(
                code_in=validate_code, user_id=user_id
            ):
                update_rows_quantity = (
                    await self.__user_repository.register_user(
                        user_id=user_id,
                    )
                )

                if update_rows_quantity == 0:
                    raise UserDoesNotExistsError(
                        "User with this id doesn't exists."
                    )

                return True

            return False

        except ValidateVerificationKeyError as error:
            raise error
        except UserIntegrityError as error:
            raise error
        except UserDBError as error:
            raise error
