"""
The file of the dependencies, that are using by these endpoints
"""

from http import HTTPStatus
from pathlib import Path

from fastapi import Depends, HTTPException, Request, WebSocket
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_405_METHOD_NOT_ALLOWED

# project configuration file
from core.config import auth_settings
from core.logger.logger import get_configure_logger
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
from services.auth_service import AuthService
from services.classes.token import Token, TokenPayload
from services.email_verification_service import (
    EmailVerificationService,
    email_verification_service_dependency,
)
from services.user_service import UserService

logger = get_configure_logger(Path(__file__).stem)


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
    token_repo: TokenRepository = Depends(token_repository_dependency),
    user_service: UserService = Depends(user_service_dependency),
) -> AuthService:
    """FastAPI dependency that provides an AuthMaster instance.

    Args:
        token_service: TokenService instance for managing refresh tokens.

    Returns:
        Configured AuthMaster instance.
    """
    return AuthService(
        token_repository=token_repo,
        user_service=user_service,
        access_secret_key=auth_settings.access_secret_key,
        refresh_secret_key=auth_settings.refresh_secret_key,
        algorithm=auth_settings.algorithm,
    )


def auth_dependency(
    request: Request = None,  # type: ignore
    websocket: WebSocket = None,  # type: ignore
    auth_master: AuthService = Depends(auth_master_dependency),
) -> TokenPayload:
    """FastAPI dependency that provides auth checking

    Args:
        auth_master: AuthMaster instance for managing access tokens.

    Returns:
        AuthMaster function for checking auth.
    """
    if request:
        source = request
    elif websocket:
        source = websocket
    else:
        raise HTTPException(
            status_code=HTTP_405_METHOD_NOT_ALLOWED,
            detail="Allowed only HTTP and WS requests",
        )

    try:
        access_token = source.cookies.get(auth_settings.access_cookie_name)
        if not access_token:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Access token not found in cookies.",
            )
        return auth_master.validate_access_token(
            token=Token(token=access_token)
        )
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
