"""
The main configuration file of the backend project part.
"""

from enum import StrEnum, auto
from logging import INFO

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict

THIRTY_DAYS_IN_MINUTES = 42000


class ModeEnum(StrEnum):
    TEST = auto()
    DEV = auto()
    PROD = auto()


# Base config class
class ModelConfig(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=(".prod.env", "../.prod.env", ".env", "../.env"),
        env_file_encoding="utf-8",
        # ignore extra vars in the env file
        extra="ignore",
    )


class AppSettings(ModelConfig):
    app_mode: ModeEnum = Field(
        default=ModeEnum.PROD, validation_alias="APP_MODE"
    )


class HostSettings(ModelConfig):
    # validation_alias – is environment variable, thats python will read, if it's exists
    host: str = Field(default="localhost", validation_alias="APP_HOST")
    port: int = Field(default=8000, validation_alias="APP_PORT")
    is_reload: bool = Field(
        default=True, validation_alias="IS_APP_AUTO_RELOAD"
    )


class AuthSettings(ModelConfig):
    access_secret_key: str = Field(
        default="my-cool-access-secret-key",
        validation_alias="ACCESS_SECRET_KEY",
    )
    refresh_secret_key: str = Field(
        default="my-cool-refresh-secret-key",
        validation_alias="REFRESH_SECRET_KEY",
    )
    access_cookie_name: str = Field(
        default="access_token", validation_alias="ACCESS_COOKIE_NAME"
    )
    refresh_cookie_name: str = Field(
        default="refresh_token", validation_alias="REFRESH_COOKIE_NAME"
    )
    algorithm: str = Field(default="HS256", validation_alias="APP_ALGORITHM")
    token_type: str = Field(default="bearer", validation_alias="TOKEN_TYPE")
    access_token_expire_minutes: int = Field(
        default=30, validation_alias="ACCESS_TOKEN_EXPIRES_MINUTES"
    )
    refresh_token_expire_minutes: int = Field(
        default=THIRTY_DAYS_IN_MINUTES,
        validation_alias="REFRESH_TOKEN_EXPIRES_MINUTES",
        description="In default 30 days (43200 minutes)",
    )


class DBSettings(ModelConfig):
    db_type: str = Field(default="postgresql", validation_alias="DB_TYPE")
    db_host: str = Field(default="localhost", validation_alias="DB_HOST")
    db_port: str = Field(default="5432", validation_alias="DB_PORT")
    db_driver: str = Field(default="asyncpg", validation_alias="DB_DRIVER")
    db_user: str = Field(default="root", validation_alias="DB_USER")
    db_user_password: str = Field(
        default="root", validation_alias="DB_PASSWORD"
    )
    db_name: str = Field(default="db", validation_alias="DB_NAME")
    db_echo: bool = Field(default=False, validation_alias="DB_ECHO")

    @property
    def db_url(self):
        return (
            f"{self.db_type}+{self.db_driver}://"
            f"{self.db_user}:{self.db_user_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


class LoggingSettings(ModelConfig):
    log_directory: str = Field(
        default="logs", validation_alias="LOG_DIRECTORY"
    )
    log_level: int = Field(default=INFO, validation_alias="LOG_LEVEL")
    date_format: str = Field(
        default="%Y-%m-%d %H:%M:%S", validation_alias="DATE_FORMAT"
    )
    log_format: str = Field(
        default="[%(asctime)s.%(msecs)03d] %(name)-30s:%(lineno)-3d %(levelname)-7s - %(message)s",
        validation_alias="LOG_FORMAT",
    )
    log_roating: str = Field(
        default="midnight", validation_alias="LOG_ROTATING"
    )
    backup_count: int = Field(
        default=30,
        validation_alias="BACKUP_COUNT",
        description=(
            "Interval of backup/roating logs. Default 30 midnights."
            + "31st log will ovverides the first log."
        ),
    )
    utc: bool = Field(default=True, validation_alias="LOG_UTC")


# create config instances
host_settings = HostSettings()
auth_settings = AuthSettings()
db_settings = DBSettings()
log_settings = LoggingSettings()
app_settings = AppSettings()
