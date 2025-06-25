from http import HTTPStatus
from pathlib import Path

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response

from api.v1.depends import (
    auth_dependency,
    auth_master_dependency,
    user_service_dependency,
)
from core.logger.logger import get_configure_logger
from domain.entities.auth_master import AuthMaster
from domain.entities.user import UserBase, UserCreate, UserCreds
from domain.exceptions import (
    InvalidTokenDataError,
    RefreshTokenAbsenceError,
    RefreshTokenBlackListError,
    RefreshTokenCreationError,
    RefreshTokenIdAbsenceError,
    TokenSessionExpiredError,
)
from schemas.token_schema import TokensResponse
from schemas.user_schema import UserCreateRequest, UserCredsRequest
from use_cases.user_service import UserService

logger = get_configure_logger(Path(__file__).stem)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/token/",
    response_model=TokensResponse,
    description=(
        "Get JSON web tokens. In other words, login in the system."
        + "On success the system automatically set tokens into the cookies"
    ),
    responses={
        200: {
            "description": "The user successfully authenticated (get the JSON web tokens)."
        },
        401: {"description": "The user password or login is incorrect."},
    },
)
async def get_tokens(
    response: Response,
    user_in: UserCredsRequest = Body(),
    user_service: UserService = Depends(user_service_dependency),
    auth_master: AuthMaster = Depends(auth_master_dependency),
):
    """
    Get JWT by user creds.
    """
    try:
        # get user hash password from database
        user_creds: UserCreds | None = await user_service.get_user_creds(
            login=user_in.login
        )
        if not user_creds:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Login or password is incorrect.",
            )

        # validate user password
        if auth_master.verify_password(
            password_in=user_in.password, password_hash=user_creds.password
        ):
            # on success generate and return JWT:
            user = UserBase(**user_creds.model_dump())

            tokens = await auth_master.generate_and_set_tokens(
                user=user, response=response
            )
            access_token, refresh_token = tokens.values()

            return TokensResponse(
                access_token=str(access_token),
                refresh_token=str(refresh_token),
            )

        # else return 403 error
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Login or password is incorrect.",
        )
    except RefreshTokenIdAbsenceError:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_CONTENT,
            detail="JWT token must contains the token_id",
        ) from RefreshTokenIdAbsenceError
    except RefreshTokenCreationError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Error with creating JWT token",
        ) from RefreshTokenCreationError


@router.post("/register/", status_code=HTTPStatus.CREATED)
async def register_user(
    response: Response,
    user_in: UserCreateRequest = Body(),
    user_service: UserService = Depends(user_service_dependency),
    auth_master: AuthMaster = Depends(auth_master_dependency),
):
    try:
        hashed_password = auth_master.hash_password(password=user_in.password)
        user = await user_service.create_user(
            user=UserCreate(
                login=user_in.login,
                password=hashed_password,
            )
        )

        tokens = await auth_master.generate_and_set_tokens(
            user=user, response=response
        )
        access_token, refresh_token = tokens.values()

        return TokensResponse(
            access_token=str(access_token),
            refresh_token=str(refresh_token),
        )

    except Exception as error:
        logger.error("Error %s", error, exc_info=error)
        return error


@router.post("/refresh/", response_model=TokensResponse)
async def refresh_tokens(
    request: Request,
    response: Response,
    auth_master: AuthMaster = Depends(auth_master_dependency),
):
    """Refresh access token and rotate refresh-token.

    Args:
        request: FastAPI request object.
        response: FastAPI response object.
        auth_master: AuthMaster dependency.

    Returns:
        TokensResponse: Response containing access and refresh tokens.
    """
    try:
        # this function will take decoded jwt from the cookies
        refresh_token_payload = (
            await auth_master.get_refresh_token_from_cookies(request=request)
        )

        # if the refresh cookie successfully validated
        # then generate new payloads and JWT
        user = UserBase(**refresh_token_payload.model_dump())

        tokens = await auth_master.generate_and_set_tokens(
            user=user, response=response
        )
        access_token, refresh_token = tokens.values()

        return TokensResponse(
            access_token=str(access_token),
            refresh_token=str(refresh_token),
        )
    except (
        TokenSessionExpiredError,
        InvalidTokenDataError,
        RefreshTokenBlackListError,
    ) as error:
        logger.debug(error, exc_info=error)
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=str(error),
        ) from error
    except (RefreshTokenIdAbsenceError, RefreshTokenAbsenceError) as error:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except RefreshTokenCreationError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Error with creating JWT token",
        ) from RefreshTokenCreationError


@router.get("/protected")
def protecded_example(auth_dependency=Depends(auth_dependency)):
    return {"status": "success"}
