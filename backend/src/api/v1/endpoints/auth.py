from http import HTTPStatus
from pathlib import Path
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Request,
    Response,
    WebSocket,
)
from pydantic import EmailStr
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from api.v1.depends import (
    auth_dependency,
    auth_master_dependency,
    user_service_dependency,
)
from core.config import app_settings, auth_settings
from core.logger.logger import get_configure_logger
from domain.exceptions import (
    InvalidTokenDataError,
    RateLimitingError,
    RefreshTokenAbsenceError,
    RefreshTokenBlackListError,
    RefreshTokenCreationError,
    RefreshTokenIdAbsenceError,
    TokenDatabaseError,
    TokenSessionExpiredError,
    UserAlreadyExistsError,
    UserDBError,
    UserDoesNotExistsError,
    UserIntegrityError,
    ValidateVerificationKeyError,
)
from schemas.token_schema import TokensResponse
from schemas.user_schema import (
    UserCreateSchema,
    UserCredsRequest,
    UserVerifyCode,
)
from services.auth_service import AuthService
from services.classes.token import Token, TokenPayload
from services.email_verification_service import (
    EmailVerificationService,
    email_verification_service_dependency,
)
from services.user_service import UserService

logger = get_configure_logger(Path(__file__).stem)

router = APIRouter(prefix="/auth", tags=["auth"])


def get_refresh_token_from_cookie(
    source: Request | WebSocket,
) -> Token:
    """Retrieve the 'refresh_token' from the cookies of a Request
    or WebSocket object.

    Raises HTTPException 401 if the token is not found.
    """
    refresh_token = source.cookies.get(auth_settings.refresh_cookie_name)
    if not refresh_token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookies.",
        )
    return Token(token=refresh_token)


def set_jwt_to_cookies(
    response: Response, access_token: Token, refresh_token: Token
) -> None:
    """Set access and refresh tokens as HTTPOnly cookies.

    Args:
        response: FastAPI Response object to set cookies.
        access_token: Token object containing the access JWT.
        refresh_token: Token object containing the refresh JWT.
    """
    secure = True

    # max age for cookie calculated in seconds
    max_age_access = auth_settings.access_token_expire_minutes * 60
    max_age_refresh = auth_settings.refresh_token_expire_minutes * 60
    response.set_cookie(
        key=auth_settings.access_cookie_name,
        value=str(access_token),
        httponly=True,
        secure=secure,
        samesite="strict",
        max_age=max_age_access,
    )
    response.set_cookie(
        key=auth_settings.refresh_cookie_name,
        value=str(refresh_token),
        httponly=True,
        secure=secure,
        samesite="strict",
        max_age=max_age_refresh,
    )


def clear_cookies(response: Response):
    response.delete_cookie(
        key=auth_settings.access_cookie_name,
        httponly=True,
    )
    response.delete_cookie(
        key=auth_settings.refresh_cookie_name,
        httponly=True,
    )


@router.post(
    "/token",
    response_model=TokensResponse,
    summary="User Login",
    description=(
        "Authenticates a user with provided credentials (login and password)."
        " Upon successful authentication, returns new access and refresh tokens."
        " For browser clients, these tokens are also set as HTTP-only cookies."
    ),
    responses={
        HTTPStatus.OK: {
            "description": "User successfully authenticated, JWT tokens returned and set in cookies."
        },
        HTTPStatus.UNAUTHORIZED: {
            "description": "Invalid login or password provided."
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Validation error, e.g., missing token ID in JWT data."
        },
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "description": "An unexpected error occurred during token creation or server operation."
        },
    },
)
async def get_tokens(
    request: Request,
    response: Response,
    user_in: UserCredsRequest = Body(),
    auth_master: AuthService = Depends(auth_master_dependency),
):
    """
    Get JWT by user creds.
    """
    try:
        if tokens := await auth_master.get_tokens_by_creds(
            user_in=user_in,
            ip=request.client.host if request.client else None,
        ):
            access_token, refresh_token = tokens.values()

            # set jwt to cookies for web systems
            set_jwt_to_cookies(
                response=response,
                access_token=access_token,
                refresh_token=refresh_token,
            )

            # for other systems
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


@router.post(
    "/register/",
    status_code=HTTPStatus.CREATED,
    response_model=TokensResponse,
    summary="User Registration",
    description=(
        "Registers a new user in the system with provided details (login, email, password)."
        " Upon successful registration, returns new access and refresh tokens."
        " For browser clients, these tokens are also set as HTTP-only cookies."
    ),
    responses={
        HTTPStatus.CREATED: {
            "description": "User successfully registered, JWT tokens returned and set in cookies."
        },
        HTTPStatus.CONFLICT: {
            "description": "User with provided login or email already exists, or an integrity constraint is violated."
        },
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "description": "An unexpected error occurred during user registration or token creation."
        },
    },
)
async def register_user(
    response: Response,
    request: Request,
    user_in: UserCreateSchema = Body(),
    auth_master: AuthService = Depends(auth_master_dependency),
):
    try:
        if tokens := await auth_master.register_user(
            user_in=user_in,
            ip=request.client.host if request.client else None,
        ):
            access_token, refresh_token = tokens.values()
            # set jwt to cookies for web systems
            set_jwt_to_cookies(
                response=response,
                access_token=access_token,
                refresh_token=refresh_token,
            )
            # for other systems
            return TokensResponse(
                access_token=str(access_token),
                refresh_token=str(refresh_token),
            )

        logger.error("Tokens doesn't returns when register user %s", user_in)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error with registration method.",
        )

    except UserDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except UserAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except UserIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except Exception as error:
        logger.error("Error %s", error, exc_info=error)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from error


@router.post(
    "/refresh",
    response_model=TokensResponse,
    summary="Refresh Access Token and Rotate Refresh Token",
    description=(
        "Refreshes the user's access token and rotates the refresh token."
        " The old refresh token is invalidated and a new one is issued."
        " The refresh token is expected to be provided in an HTTP-only cookie."
    ),
    responses={
        HTTPStatus.OK: {
            "description": "Tokens successfully refreshed and new tokens returned/set in cookies."
        },
        HTTPStatus.UNAUTHORIZED: {
            "description": "Refresh token is invalid or not found in cookies."
        },
        HTTPStatus.FORBIDDEN: {
            "description": "Refresh token session expired, invalid data, or token is blacklisted."
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Validation error, e.g., refresh token ID is missing or token is entirely absent."
        },
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "description": "An unexpected error occurred during token creation or server operation."
        },
    },
)
async def refresh_tokens(
    request: Request,
    response: Response,
    auth_master: AuthService = Depends(auth_master_dependency),
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
        # get refresh token from cookies or from request
        refresh_token = get_refresh_token_from_cookie(source=request)

        if tokens := await auth_master.rotate_tokens(
            refresh_token=refresh_token
        ):
            access_token, refresh_token = tokens.values()

            # set tokens in the cookies (for web system)
            set_jwt_to_cookies(
                response=response,
                access_token=access_token,
                refresh_token=refresh_token,
            )

            # for other systems
            return TokensResponse(
                access_token=str(access_token),
                refresh_token=str(refresh_token),
            )

        # else return 403 error
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Refresh token is invalid.",
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


@router.get(
    "/get_user_id",
    summary="Get Current User ID",
    description="Retrieves the unique identifier (UUID) of the authenticated user from their access token.",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully retrieved the user ID.",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            },
        },
        HTTPStatus.UNAUTHORIZED: {
            "description": "Authentication required or invalid access token."
        },
    },
)
async def get_user_id(jwt: TokenPayload = Depends(auth_dependency)):
    return {"user_id": jwt.user_id}


@router.post(
    "/send_verification_code/email",
    summary="Send Email Verification Code",
    description=(
        "Sends a one-time verification code to the specified email address of the authenticated user."
        " This code is used to verify the user's email for registration or other purposes."
        " Requires an authenticated session."
    ),
    responses={
        HTTPStatus.OK: {
            "description": "Verification code successfully sent to the email.",
            "content": {
                "application/json": {
                    "example": {"message": "Verification code sent"}
                }
            },
        },
        HTTPStatus.UNAUTHORIZED: {
            "description": "Authentication required or user integrity error (e.g., email already verified)."
        },
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "description": "An error occurred during the verification code operation, possibly due to rate limiting or mail service issues."
        },
    },
)
async def send_email_verification_code(
    email: EmailStr,
    jwt: TokenPayload = Depends(auth_dependency),
    email_verification_service: EmailVerificationService = Depends(
        email_verification_service_dependency
    ),
):
    try:
        await email_verification_service.set_verification_code(
            email=email,
            user_id=UUID(jwt.user_id),
        )
        return {"message": "Verification code sent"}
    except UserIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error
    except RateLimitingError as error:
        logger.error("Error with verification operation.", exc_info=error)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error with code operations.",
        ) from error


@router.post(
    "/verify_code/email",
    summary="Verify Email Code and Register User",
    description=(
        "Verifies the provided email verification code for the authenticated user."
        " If the code is valid, the user's account is marked as 'registered'."
        " This is typically the final step of the email verification process."
    ),
    responses={
        HTTPStatus.OK: {
            "description": "Email verification successful, user account marked as registered.",
            "content": {
                "application/json": {"example": {"status": "success"}}
            },
        },
        HTTPStatus.UNAUTHORIZED: {
            "description": "Invalid verification token or code provided."
        },
        HTTPStatus.NOT_FOUND: {
            "description": "The user associated with the token does not exist."
        },
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "description": "An internal server error occurred during code validation or database update (e.g., user integrity or DB error)."
        },
    },
)
async def verify_email_code(
    user_verify_data: UserVerifyCode,
    jwt: TokenPayload = Depends(auth_dependency),
    user_service: UserService = Depends(user_service_dependency),
):
    try:
        is_user_registered = await user_service.register_user(
            user_id=UUID(jwt.user_id),
            validate_code=str(user_verify_data.code),
        )

        if not is_user_registered:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Token is invalid.",
            )

        return {"status": "success"}

    except UserDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ValidateVerificationKeyError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error when validate token.",
        ) from error
    except UserIntegrityError as error:
        raise HTTPException(
            # 500 code, because user_integriry_error don't should
            # to raises in the register scenario
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        ) from error
    except UserDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error when validate token.",
        ) from error


@router.post(
    "/exit",
    status_code=HTTP_204_NO_CONTENT,
    summary="Logout / Close User Session",
    description=(
        "Invalidates the current refresh token associated with the authenticated session"
        " and clears authentication cookies from the client (access and refresh tokens)."
        " This effectively logs the user out."
    ),
    responses={
        HTTPStatus.OK: {
            "description": "User session successfully closed and cookies cleared."
        },
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "description": "An error occurred while invalidating the token in the database."
        },
    },
)
async def close_session(
    response: Response,
    jwt: TokenPayload = Depends(auth_dependency),
    auth_service: AuthService = Depends(auth_master_dependency),
):
    try:
        clear_cookies(response)
        await auth_service.close_session(token_id=UUID(jwt.token_id))
    except TokenDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error when close session.",
        ) from error
