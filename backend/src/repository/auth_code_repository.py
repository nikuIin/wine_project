from datetime import timedelta
from pathlib import Path
from uuid import UUID

from redis.asyncio import Redis

from core.general_constants import (
    CODE_LE_VALUE,
    CODE_LEN,
    CODE_REQUEST_LOCK_TIME_IN_SECONDS,
    FIFTEEN_MINUTES_IN_SECONDS,
    ONE_HOUR_IN_SECONDS,
)
from core.logger.logger import get_configure_logger
from db.dependencies.redis_helper import redis_helper

logger = get_configure_logger(Path(__file__).stem)


class AuthCodeRepository:
    def __init__(self, redis: Redis):
        """Initialize the CodeRepository with a Redis client.

        Args:
            redis (Redis): An asynchronous Redis client instance.
        """
        self.__redis = redis

    async def __set_rate_limit(
        self,
        key: str,
        rate_limit: int,
        ttl: int | timedelta = ONE_HOUR_IN_SECONDS,
    ) -> None:
        """Set a rate limit value in Redis for a specific key.

        This is a private helper method to abstract the Redis key creation
        and the `setex` command.

        Args:
            key (str): The unique identifier for the rate limit
            (e.g., user ID or email).
            rate_limit (int): The value to set for the rate limit count.
            ttl (int | timedelta): The time-to-live for the key in seconds
            or as a timedelta object. Defaults to 3600 seconds (one hour).
        """
        rate_limit_key = f"rate_limit:{key}"
        await self.__redis.setex(
            name=rate_limit_key, value=rate_limit, time=ttl
        )

    async def __get_rate_limit(self, key: str) -> int:
        """Get a rate limit value from Redis for a specific key.

        This is a private helper method to abstract the Redis key creation
        and the `get` command.

        Args:
            key (str): The unique identifier for the rate limit
            (e.g., user ID or email).

        Returns:
            int: The current rate limit value from Redis.
        """

        # === main logic ===
        rate_limit_key = f"rate_limit:{key}"
        try:
            rate_limit = await self.__redis.get(rate_limit_key)
            rate_limit = int(rate_limit) if rate_limit else 0

            return rate_limit

        # === errors handling ===
        except ValueError as error:
            logger.warning(
                "get_rate_limit function return str instead int",
                exc_info=error,
            )
            raise error

    async def set_email_blocked(
        self,
        email: str,
        ttl: int | timedelta = CODE_REQUEST_LOCK_TIME_IN_SECONDS,
    ) -> None:
        """Set an email address as blocked for getting code in Redis.

        Args:
            email (str): The email address to block.
            ttl (int | timedelta): The time-to-live for the block entry
                in seconds or as a timedelta object. Defaults to 1 minute.

        Raises:
            ConnectionError: On Redis connection failure.
            TimeoutError: On Redis operation timeout.
            ConnectionResetError: On Redis connection reset.
        """
        try:
            await self.__redis.setex(name=email, value="blocked", time=ttl)

        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            logger.error(
                "Error with redis when set email to block.", exc_info=error
            )
            raise error

    async def is_email_blocked(self, email: str) -> bool:
        """Check if an email address is currently blocked in Redis.

        Args:
            email (str): The email address to check for blockage.

        Returns:
            bool: True if the email is blocked, False otherwise.

        Raises:
            ConnectionError: On Redis connection failure.
            TimeoutError: On Redis operation timeout.
            ConnectionResetError: On Redis connection reset.
        """
        try:
            email = await self.__redis.get(email)
            return email is not None
        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            logger.error(
                "Error with redis when delete rate limit key", exc_info=error
            )
            raise error

    async def delete_rate_limit(self, key: str) -> None:
        try:
            await self.__redis.delete(f"rate_limit:{key}")
        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            logger.error(
                "Error with redis when delete rate limit key", exc_info=error
            )
            raise error

    async def get_user_rate_limit(
        self,
        user_id: UUID,
    ) -> int:
        """Get the rate limit for a specific user.

        Args:
            user_id (UUID): The unique identifier for the user.

        Returns:
            int: The current rate limit value for user from Redis.

        Raises:
            ConnectionError: On Redis connection failure.
            TimeoutError: On Redis operation timeout.
            ConnectionResetError: On Redis connection reset.
        """
        try:
            rate_limit = await self.__get_rate_limit(key=str(user_id))
            logger.info(
                "Rate limit for authentificate user: %s: %s",
                user_id,
                rate_limit,
            )
            return rate_limit

        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            logger.error(
                "Error with redis when get rate limit to user_id %s",
                user_id,
                exc_info=error,
            )
            raise error

    async def set_user_rate_limit(
        self,
        user_id: UUID,
        rate_limit: int,
        ttl: int | timedelta = FIFTEEN_MINUTES_IN_SECONDS,
    ) -> None:
        """Set the rate limit for a specific user.

        Args:
            user_id (UUID): The unique identifier for the user.
            rate_limit (int): The rate limit count to set.
            ttl (int | timedelta): The time-to-live for the rate limit.
                Defaults to 900 seconds (15 minutes).

        Raises:
            ConnectionError: On Redis connection failure.
            TimeoutError: On Redis operation timeout.
            ConnectionResetError: On Redis connection reset.
        """
        logger.info(
            "Attemt to connect to the system from id %s: %s",
            user_id,
            rate_limit,
        )
        try:
            await self.__set_rate_limit(
                key=str(user_id), rate_limit=rate_limit, ttl=ttl
            )

        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            logger.error(
                "Error with redis when set rate limit to user_id %s"
                + " with ttl=%s",
                user_id,
                ttl,
                exc_info=error,
            )
            raise error

    async def get_email_rate_limit(
        self,
        email: str,
    ) -> int:
        """Get the rate limit for a specific email address.

        Args:
            email (EmailStr): The email address to check the rate limit
                for.

        Returns:
            int: The current rate limit value for the email from Redis.

        Raises:
            ConnectionError: On Redis connection failure.
            TimeoutError: On Redis operation timeout.
            ConnectionResetError: On Redis connection reset.
        """

        try:
            email_rate = await self.__get_rate_limit(key=str(email))
            logger.info(
                "Rate limit for authentificate with email%s: %s",
                email,
                email_rate,
            )
            return email_rate

        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            logger.error(
                "Error with redis when get rate limit", exc_info=error
            )
            raise error

    async def set_email_rate_limit(
        self,
        email: str,
        rate_limit: int,
        ttl: int | timedelta = ONE_HOUR_IN_SECONDS,
    ) -> None:
        """Set the rate limit for a specific email address.

        Args:
            email (EmailStr): The email address to set the rate limit
                for.
            rate_limit (int): The rate limit count to set.
            ttl (int | timedelta): The time-to-live for the rate limit.
                Defaults to 3600 seconds (one hour).

        Raises:
            ConnectionError: On Redis connection failure.
            TimeoutError: On Redis operation timeout.
            ConnectionResetError: On Redis connection reset.
        """
        try:
            await self.__set_rate_limit(
                key=str(email),
                rate_limit=rate_limit,
                ttl=ttl,
            )
        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            logger.error(
                "Error with redis when set rate limit", exc_info=error
            )
            raise error

    async def set_verification_code(
        self,
        verification_code: str,
        user_id: UUID,
        ttl: int = FIFTEEN_MINUTES_IN_SECONDS,
    ) -> None:
        try:
            redis_key = f"token_verify:{user_id}"
            await self.__redis.setex(
                name=redis_key,
                value=verification_code,
                time=ttl,
            )
        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            # we dont set exc_info because we can't log the verification key
            logger.error(
                "Error with redis when set verification key for user %s",
                user_id,
                exc_info=error,
            )
            raise error

    async def get_verification_code(
        self,
        user_id: UUID,
    ) -> bytes:
        try:
            redis_key = f"token_verify:{user_id}"
            return await self.__redis.get(name=redis_key)
        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            logger.error(
                "Error with redis when get verification key for user %s",
                user_id,
                exc_info=error,
            )
            raise error

    async def delete_verification_code(
        self,
        user_id: UUID,
    ) -> None:
        try:
            redis_key = f"token_verify:{user_id}"
            return await self.__redis.delete(redis_key)
        except (ConnectionError, TimeoutError, ConnectionResetError) as error:
            # we dont set exc_info because we can't log the verification key
            logger.error(
                "Error with redis when delete verification key for user %s",
                user_id,
                exc_info=error,
            )
            raise error


def auth_code_repository_dependency():
    return AuthCodeRepository(redis=redis_helper.redis)
