from datetime import timedelta
from hashlib import md5
from pathlib import Path
from secrets import randbelow
from uuid import UUID

from fastapi import Depends
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from core.config import auth_settings, mail_settings
from core.general_constants import (
    CODE_LE_VALUE,
    CODE_LEN,
    CODE_REQUEST_LOCK_TIME_IN_SECONDS,
    FIFTEEN_MINUTES_IN_SECONDS,
)
from core.logger.logger import get_configure_logger
from domain.exceptions import (
    DeleteVerificationKeyError,
    EmailDBError,
    EmailRateLimitingError,
    GetVerificationKeyError,
    NextCodeAttemptNotPassedError,
    SetVerificationKeyError,
    UserDBError,
    UserDoesNotExistsError,
    UserIntegrityError,
    UserRateLimitingError,
    ValidateVerificationKeyError,
)
from repository.auth_code_repository import (
    AuthCodeRepository,
    auth_code_repository_dependency,
)
from repository.user_repository import (
    UserRepository,
    user_repository_dependency,
)

logger = get_configure_logger(Path(__file__).stem)

# TODO: add abastact class for verification services
# (examples of subclasses are phone, email, may be telegram, etc.)


MAX_USER_AUTH_ATTEMPTS_PER_TIME = 5
MAX_EMAIL_AUTH_ATTEMPTS_PER_TIME = 5


class EmailVerificationService:
    def __init__(
        self,
        auth_code_repository: AuthCodeRepository,
        user_repository: UserRepository,
        fast_mail: FastMail,
    ):
        self.__auth_code_repository = auth_code_repository
        self.__user_repository = user_repository
        self.__fast_mail = fast_mail

    def _generate_code(self) -> str:
        return str(randbelow(CODE_LE_VALUE)).zfill(CODE_LEN)

    def _generate_hashed_verification_code(
        self, code: str, salt: str = auth_settings.salt
    ) -> str:
        return md5((code + salt).encode()).hexdigest()

    def _get_hashed_email(
        self, email: EmailStr, salt: str = auth_settings.salt
    ) -> str:
        return md5((email + salt).encode()).hexdigest()

    async def _is_email_belong_to_user(
        self,
        user_id: UUID,
        email_in: EmailStr,
    ) -> bool:
        try:
            email = await self.__user_repository.get_user_email(
                user_id=user_id
            )

            return email_in == email

        except UserDoesNotExistsError as error:
            raise error
        except UserIntegrityError as error:
            raise error
        except UserDBError as error:
            raise error

    async def _store_verification_code(
        self,
        code: str,
        user_id: UUID,
    ) -> None:
        try:
            await self.__auth_code_repository.set_verification_code(
                user_id=user_id,
                verification_code=code,
                ttl=FIFTEEN_MINUTES_IN_SECONDS,
            )
        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            raise SetVerificationKeyError from error

    async def _user_rate_limit(self, user_id: UUID) -> int:
        return await self.__auth_code_repository.get_user_rate_limit(
            user_id=user_id
        )

    async def _email_rate_limit(self, email_hash: str) -> int:
        return await self.__auth_code_repository.get_email_rate_limit(
            email=email_hash
        )

    async def _set_new_email_rate_limit(self, email: str, rate_limit) -> None:
        await self.__auth_code_repository.set_email_rate_limit(
            email=email, rate_limit=rate_limit
        )

    async def _set_new_user_rate_limit(
        self, user_id: UUID, rate_limit
    ) -> None:
        await self.__auth_code_repository.set_user_rate_limit(
            user_id=user_id, rate_limit=rate_limit
        )

    async def _validate_attempt_quantity(
        self, email: str, user_id: UUID
    ) -> tuple[int, int]:
        if (
            user_rate_limit := await self._user_rate_limit(user_id=user_id)
        ) >= MAX_USER_AUTH_ATTEMPTS_PER_TIME:
            raise UserRateLimitingError
        if (
            email_rate_limit := await self._email_rate_limit(email_hash=email)
        ) >= MAX_EMAIL_AUTH_ATTEMPTS_PER_TIME:
            raise EmailRateLimitingError

        return user_rate_limit, email_rate_limit

    async def _send_verification_code(self, email: EmailStr, code: str):
        message = MessageSchema(
            subject="Verification Code",
            recipients=[email],
            body=f"<p>Verification code: <b>{code}</b></p>",
            subtype=MessageType.html,
        )
        await self.__fast_mail.send_message(message=message)

    async def _is_сode_resend_available(self, hash_email: str):
        try:
            return not await self.__auth_code_repository.is_email_blocked(
                email=hash_email
            )
        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            raise EmailDBError from error

    async def _set_code_request_lock(
        self,
        hash_email: str,
        ttl: int | timedelta = CODE_REQUEST_LOCK_TIME_IN_SECONDS,
    ):
        try:
            return await self.__auth_code_repository.set_email_blocked(
                email=hash_email, ttl=ttl
            )
        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            raise EmailDBError from error

    async def set_verification_code(
        self,
        email: EmailStr,
        user_id: UUID,
    ) -> None:
        """Unite point of verification code methods by email"""
        email_hash = self._get_hashed_email(email=email)

        if not await self._is_сode_resend_available(hash_email=email_hash):
            raise NextCodeAttemptNotPassedError

        # check that email belongs to user
        if not await self._is_email_belong_to_user(
            user_id=user_id, email_in=email
        ):
            raise UserIntegrityError(f"Email {email} doens't belong to user.")

        # check if the attempt of auth is valid
        user_rate, email_rate = await self._validate_attempt_quantity(
            email=email_hash, user_id=user_id
        )

        # increate user and email limit for auth
        user_rate += 1
        email_rate += 1

        # set new rate limit
        await self._set_new_email_rate_limit(
            email=email_hash, rate_limit=email_rate
        )
        await self._set_new_user_rate_limit(
            user_id=user_id, rate_limit=user_rate
        )

        code = self._generate_code()
        hashed_code = self._generate_hashed_verification_code(code=code)

        # store in the redis
        await self._store_verification_code(
            code=hashed_code,
            user_id=user_id,
        )

        # send to email
        await self._send_verification_code(email=email, code=code)

        # set the block to get new code until the time passed
        await self._set_code_request_lock(hash_email=email_hash)

    async def _clear_verification_code(self, user_id: UUID):
        try:
            await self.__auth_code_repository.delete_verification_code(
                user_id=user_id,
            )
        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            raise DeleteVerificationKeyError from error

    async def _get_stored_verification_code(self, user_id: UUID) -> str:
        try:
            return str(
                await self.__auth_code_repository.get_verification_code(
                    user_id=user_id,
                )
            )
        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            raise GetVerificationKeyError from error

    def _verify_hash(
        self,
        hash: str,
        verified_data: str,
        salt: str = auth_settings.salt,
    ):
        return hash == md5((verified_data + salt).encode()).hexdigest()

    async def validate_verification_code(
        self, code_in: str, user_id: UUID
    ) -> bool:
        try:
            # data preparation
            code_hash = await self._get_stored_verification_code(
                user_id=user_id
            )

            if self._verify_hash(code_hash, code_in):
                await self._clear_verification_code(user_id=user_id)
                return True

            return False

        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            raise ValidateVerificationKeyError from error


def fast_mail_dependency() -> FastMail:
    return FastMail(mail_settings.mail_config)


def email_verification_service_dependency(
    auth_code_repository=Depends(auth_code_repository_dependency),
    fast_email=Depends(fast_mail_dependency),
    user_repository=Depends(user_repository_dependency),
):
    return EmailVerificationService(
        auth_code_repository=auth_code_repository,
        fast_mail=fast_email,
        user_repository=user_repository,
    )
