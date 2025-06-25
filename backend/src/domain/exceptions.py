"""
The custom exceptions of the project.
"""

from pathlib import Path

from core.logger.logger import get_configure_logger

logger = get_configure_logger(filename=Path(__file__).stem)


# ===============================
#         Tokens erros          #
# ===============================


class TokenSessionExpiredError(Exception):
    """The error, which occures, when the token session is expired"""

    def __init__(self, message="Token session expired."):
        super().__init__(message)


class InvalidTokenDataError(Exception):
    """The error, which occures, that the JWT-payload is invalid"""

    def __init__(self, message="Invalid JWT-payload."):
        super().__init__(message)
        logger.warning("The wrong jwt data was recieved to the server", exc_info=True)


class AccessTokenAbsenceError(Exception):
    """The error occures, while the access token wasn't finds in the cookies"""

    def __init__(self, message="The are no access token in the cookies."):
        super().__init__(message)


class RefreshTokenAbsenceError(Exception):
    """The error occures, while the refresh token wasn't finds in the cookies"""

    def __init__(self, message="The are no refresh token in the cookies."):
        super().__init__(message)


class RefreshTokenCreationError(Exception):
    """The error occures, while the refresh token wasn't created"""

    def __init__(self, message="The refresh token wasn't created."):
        super().__init__(message)


class RefreshTokenIdAbsenceError(Exception):
    """The error occures, while the refresh token payload doesn't have token_id"""

    def __init__(self, message="The refresh token id must have token_id."):
        logger.warning("The attemt of creating the refresh token without id", exc_info=True)
        super().__init__(message)


class RefreshTokenBlackListError(Exception):
    """The error occures, while the refresh token is in the black list"""

    def __init__(self, message="The refresh token is in the black list."):
        super().__init__(message)
