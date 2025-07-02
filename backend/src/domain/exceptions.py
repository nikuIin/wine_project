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
        logger.warning(
            "The wrong jwt data was recieved to the server", exc_info=True
        )


class AccessTokenAbsenceError(Exception):
    """The error occures, while the access token wasn't finds in the cookies"""

    def __init__(self, message="The are no access token in the cookies."):
        super().__init__(message)


class RefreshTokenAbsenceError(Exception):
    """The error occures, while the refresh token
    wasn't finds in the cookies

    """

    def __init__(self, message="The are no refresh token in the cookies."):
        super().__init__(message)


class RefreshTokenCreationError(Exception):
    """The error occures, while the refresh token wasn't created"""

    def __init__(self, message="The refresh token wasn't created."):
        super().__init__(message)


class RefreshTokenIdAbsenceError(Exception):
    """The error occures, while the refresh token
    payload doesn't have token_id

    """

    def __init__(self, message="The refresh token id must have token_id."):
        logger.warning(message, exc_info=True)
        super().__init__(message)


class RefreshTokenBlackListError(Exception):
    """The error occures, while the refresh token is in the black list"""

    def __init__(self, message="The refresh token is in the black list."):
        super().__init__(message)


# ===============================
#        Country errors         #
# ===============================


class CountryDBError(Exception):
    """The error ralated to the error with country data in the database."""

    def __init__(
        self,
        message="The error of adding country to the database.",
    ):
        super().__init__(message)


class CountryIntegrityError(Exception):
    """The error occures with attempt to adding
    the country_data or country_translate_dataa wich
    already exists in the database or trying adding the
    depends-data those doesn't exists.
    """

    def __init__(self, message="The integrity error of country data."):
        super().__init__(message)


class CountryDoesNotExistsError(Exception):
    """
    The error occures, while the country wasn't
    exists in the DB
    """

    def __init__(
        self,
        message=("Country with this data doesn't exists."),
    ):
        super().__init__(message)


# ===============================
#         Region erros          #
# ===============================
#


class RegionDatabaseError(Exception):
    """The error occurs with database errors relating the region table"""

    def __init__(self, message="Database region error."):
        super().__init__(message)


class RegionConflictError(Exception):
    """The error occurs when trying to create a region that already exists."""

    def __init__(
        self, message="A region with this name or ID already exists."
    ):
        super().__init__(message)


class RegionDoesNotExistsError(Exception):
    """The error occurs when there's a problem updating a region in the database."""

    def __init__(self, message="Failed to update the region in the database."):
        super().__init__(message)
