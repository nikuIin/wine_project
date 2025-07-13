from redis.asyncio import Redis

from core.config import redis_settings


class RedisHelper:
    def __init__(
        self,
        host: str,
        port: int,
        db: int,
        password: str,
        decode_responses: bool = True,
    ):
        self.__redis = Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses,
        )

    @property
    def redis(self) -> Redis:
        return self.__redis


redis_helper = RedisHelper(
    host=redis_settings.host,
    port=redis_settings.port,
    db=redis_settings.db,
    password=redis_settings.password,
)
