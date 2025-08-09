from http import HTTPStatus
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from pydantic import EmailStr
from starlette.status import (
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
from core.logger.logger import get_configure_logger
from domain.entities.token import TokenPayload
from domain.entities.user import UserBase, UserCreate, UserCreds
from domain.exceptions import (
    InvalidTokenDataError,
    RateLimitingError,
    RefreshTokenAbsenceError,
    RefreshTokenBlackListError,
    RefreshTokenCreationError,
    RefreshTokenIdAbsenceError,
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
from services.auth_master import AuthMaster
from services.email_verification_service import (
    EmailVerificationService,
    email_verification_service_dependency,
)
from services.user_service import UserService

logger = get_configure_logger(Path(__file__).stem)

router = APIRouter(prefix="/auth", tags=["auth"])


# !!!!!!!!!
# TODO: move all buiseness logic to the service layer
# !!!!!!!!!


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
    user_in: UserCreateSchema = Body(),
    user_service: UserService = Depends(user_service_dependency),
    auth_master: AuthMaster = Depends(auth_master_dependency),
):
    try:
        hashed_password = auth_master.hash_password(password=user_in.password)
        user_in.password = hashed_password

        user = await user_service.create_user(
            user=UserCreate(
                login=user_in.login,
                password=hashed_password,
                email=user_in.email,
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


@router.post("/get_verification_code/email")
async def get_email_verification_code(
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


@router.post("/verify_code/email")
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
            detail="Intenal server error when validate token.",
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
