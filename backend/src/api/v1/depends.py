"""
The file of the dependecies, that are using by these endpoints
"""

from http import HTTPStatus
from pathlib import Path

from fastapi import Depends, HTTPException, Request, WebSocket

# project configuration file
from core.config import auth_settings
from core.logger.logger import get_configure_logger
from domain.entities.token import TokenPayload
from domain.enums import LanguageEnum
from domain.exceptions import (
    AccessTokenAbsenceError,
    InvalidTokenDataError,
    TokenSessionExpiredError,
)
from repository.token_repository import (
    TokenRepository,
    token_repository_dependency,
)
from repository.user_repository import (
    UserRepository,
    user_repository_dependency,
)
from services.auth_master import AuthMaster
from services.email_verification_service import (
    EmailVerificationService,
    email_verification_service_dependency,
)
from services.token_service import TokenService
from services.user_service import UserService

logger = get_configure_logger(Path(__file__).stem)


def token_service_dependency(
    token_repository: TokenRepository = Depends(token_repository_dependency),
) -> TokenService:
    return TokenService(token_repository=token_repository)


def user_service_dependency(
    user_repository: UserRepository = Depends(user_repository_dependency),
    email_verification_service: EmailVerificationService = Depends(
        email_verification_service_dependency
    ),
):
    return UserService(
        user_repository=user_repository,
        email_verification_service=email_verification_service,
    )


def auth_master_dependency(
    token_service: TokenService = Depends(token_service_dependency),
) -> AuthMaster:
    """FastAPI dependency that provides an AuthMaster instance.

    Args:
        token_service: TokenService instance for managing refresh tokens.

    Returns:
        Configured AuthMaster instance.
    """
    return AuthMaster(
        token_service=token_service,
        access_secret_key=auth_settings.access_secret_key,
        refresh_secret_key=auth_settings.refresh_secret_key,
        algorithm=auth_settings.algorithm,
    )


def auth_dependency(
    request: Request = None,  # type: ignore
    websocket: WebSocket = None,  # type: ignore
    auth_master: AuthMaster = Depends(auth_master_dependency),
) -> TokenPayload:
    """FastAPI dependency that provides auth checking

    Args:
        auth_master: AuthMaster instance for managing access tokens.

    Returns:
        AuthMaster function for checking auth.
    """
    if request:
        connection = request
    elif websocket:
        connection = websocket
    else:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Allowed only HTTP and WS requests",
        )

    try:
        return auth_master.auth_check(request=connection)
    except (
        AccessTokenAbsenceError,
        InvalidTokenDataError,
        TokenSessionExpiredError,
    ) as error:
        logger.debug("Auth error.", exc_info=error)
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail=str(error)
        ) from error


# TODO: change return types
def language_dependency(
    request: Request, preferred_language: str | None = None
) -> LanguageEnum | str | None:
    if not preferred_language:
        request_language = request.headers.get("Accept-Language", "")

        # parse Accept-Language header
        preferred_language = request_language.split(";")[0].split(",")[0]

        # TODO: create a cycle of getting preferred languages and checking
        #  that language is in the LanguageEnum (supports in our application).
        #  Else set language to the default language

    logger.debug("Preferred accept-language header: %s.", preferred_language)

    return (
        preferred_language
        if preferred_language in LanguageEnum
        else LanguageEnum.DEFAULT_LANGUAGE
    )
