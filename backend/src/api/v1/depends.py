"""
The file of the dependecies, that are using by these endpoints
"""

from http import HTTPStatus

from fastapi import Depends, HTTPException, Request

# project configuration file
from core.config import auth_settings
from domain.entities.auth_master import AuthMaster
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
from use_cases.token_service import TokenService
from use_cases.user_service import UserService


def token_service_dependency(
    token_repository: TokenRepository = Depends(token_repository_dependency),
) -> TokenService:
    return TokenService(token_repository=token_repository)


def user_service_dependency(
    user_repository: UserRepository = Depends(user_repository_dependency),
):
    return UserService(user_repository=user_repository)


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
    request: Request, auth_master: AuthMaster = Depends(auth_master_dependency)
):
    """FastAPI dependency that provides auth checking

    Args:
        auth_master: AuthMaster instance for managing access tokens.

    Returns:
        AuthMaster function for checking auth.
    """
    try:
        auth_master.auth_check(request=request)
    except (
        AccessTokenAbsenceError,
        InvalidTokenDataError,
        TokenSessionExpiredError,
    ) as error:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail=str(error)
        ) from error
