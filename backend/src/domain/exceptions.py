"""
The custom exceptions of the project.
"""

from pathlib import Path

from core.logger.logger import get_configure_logger

logger = get_configure_logger(filename=Path(__file__).stem)


# ===============================
#         Tokens errors         #
# ===============================


class TokenSessionExpiredError(Exception):
    """The error, which occurs, when the token session is expired"""

    def __init__(self, message="Token session expired."):
        super().__init__(message)


class InvalidTokenDataError(Exception):
    """The error, which occurs, that the JWT-payload is invalid"""

    def __init__(self, message="Invalid JWT-payload."):
        super().__init__(message)
        logger.warning(
            "The wrong jwt data was receieved to the server", exc_info=True
        )


class AccessTokenAbsenceError(Exception):
    """The error occurs, while the access token wasn't finds in the cookies"""

    def __init__(self, message="The are no access token in the cookies."):
        super().__init__(message)


class RefreshTokenAbsenceError(Exception):
    """The error occurs, while the refresh token
    wasn't finds in the cookies

    """

    def __init__(self, message="The are no refresh token in the cookies."):
        super().__init__(message)


class RefreshTokenCreationError(Exception):
    """The error occurs, while the refresh token wasn't created"""

    def __init__(self, message="The refresh token wasn't created."):
        super().__init__(message)


class RefreshTokenIdAbsenceError(Exception):
    """The error occurs, while the refresh token
    payload doesn't have token_id

    """

    def __init__(self, message="The refresh token id must have token_id."):
        logger.warning(message, exc_info=True)
        super().__init__(message)


class RefreshTokenBlackListError(Exception):
    """The error occurs, while the refresh token is in the black list"""

    def __init__(self, message="The refresh token is in the black list."):
        super().__init__(message)


# ===============================
#          Email errors         #
# ===============================


class EmailDBError(Exception):
    """The error related to the error with email data in the database."""

    def __init__(
        self,
        message="The database error.",
    ):
        super().__init__(message)


# ===============================
#        Country errors         #
# ===============================


class CountryDBError(Exception):
    """The error related to the error with country data in the database."""

    def __init__(
        self,
        message="The error of adding country to the database.",
    ):
        super().__init__(message)


class CountryIntegrityError(Exception):
    """The error occurs with attempt to adding
    the country_data or country_translate_dataa which
    already exists in the database or trying adding the
    depends-data those doesn't exists.
    """

    def __init__(self, message="The integrity error of country data."):
        super().__init__(message)


class CountryDoesNotExistsError(Exception):
    """
    The error occurs, while the country wasn't
    exists in the DB
    """

    def __init__(
        self,
        message=("Country with this data doesn't exists."),
    ):
        super().__init__(message)


class CountryAlreadyExistsError(Exception):
    """The country with this data already exists in the database"""

    def __init__(
        self,
        message="The country with this data already exists in the database",
    ):
        super().__init__(message)


# ===============================
#           User errors         #
# ===============================


class UserDBError(Exception):
    """The error related to the error with user data in the database."""

    def __init__(
        self,
        message="The db error of user data.",
    ):
        super().__init__(message)


class UserIntegrityError(Exception):
    """The error occurs with attempt to adding the user."""

    def __init__(self, message="The integrity error of user data."):
        super().__init__(message)


class UserDoesNotExistsError(Exception):
    """
    The error occurs, while the user wasn't
    exists in the DB
    """

    def __init__(
        self,
        message=("User with this data doesn't exists."),
    ):
        super().__init__(message)


class UserAlreadyExistsError(Exception):
    """The user with this data already exists in the database"""

    def __init__(
        self,
        message="The user with this data already exists in the database",
    ):
        super().__init__(message)


# ===============================
#         Region errors          #
# ===============================


class RegionDatabaseError(Exception):
    """The error occurs with database errors relating the region table"""

    def __init__(self, message="Database region error."):
        super().__init__(message)


class RegionIntegrityError(Exception):
    """The error occurs with attempt to adding
    the region_data or region_translate_data which
    already exists in the database or trying adding the
    depends-data those doesn't exists.
    """

    def __init__(self, message="The integrity error of region data."):
        super().__init__(message)


class RegionAlreadyExistsError(Exception):
    """The region with this id already exists in the database"""

    def __init__(
        self, message="The region with this id already exists in the database"
    ):
        super().__init__(message)


class RegionDoesNotExistsError(Exception):
    """The region doesn't exists in the database."""

    def __init__(
        self, message="The region with this id doesn't exists in the database"
    ):
        super().__init__(message)


# ===============================
#       Language errors         #
# ===============================


class LanguageDoesNotExistsError(Exception):
    """The language doesn't exists in the database."""

    def __init__(
        self,
        message="The language with this id doesn't exists in the database",
    ):
        super().__init__(message)


# ===============================
#         Grape errors          #
# ===============================


class GrapeDatabaseError(Exception):
    """The error occurs with database errors relating the grape
    or grape_translate tables"""

    def __init__(self, message="Database grape error."):
        super().__init__(message)


class GrapeIntegrityError(Exception):
    """The error occurs when database throw
    IntegrityError after operation with grape
    or grape_translate data.
    """

    def __init__(self, message="The integrity error of grape data."):
        super().__init__(message)


class GrapeAlreadyExistsError(Exception):
    """The grape with this id already exists in the database"""

    def __init__(
        self, message="The grape with this id already exists in the database"
    ):
        super().__init__(message)


class GrapeDoesNotExistsError(Exception):
    """The grape doesn't exists in the database."""

    def __init__(
        self, message="The grape with this id doesn't exists in the database"
    ):
        super().__init__(message)


# ===================================== #
#        Email verification errors      #
# ===================================== #


class SetVerificationKeyError(Exception):
    """The error with setting verification key in the Redis"""

    def __init__(
        self, message="The internal server error when set verification key"
    ):
        super().__init__(message)


class GetVerificationKeyError(Exception):
    """The error with getting verification key in the Redis"""

    def __init__(
        self, message="The internal server error when get verification key"
    ):
        super().__init__(message)


class ValidateVerificationKeyError(Exception):
    """The error with validating verification key in the Redis"""

    def __init__(
        self, message="The internal server error when get validate key"
    ):
        super().__init__(message)


class DeleteVerificationKeyError(Exception):
    """The error with deliting verification key in the Redis"""

    def __init__(
        self, message="The internal server error with verification key"
    ):
        super().__init__(message)


class RateLimitingError(Exception):
    """The error occurs with a lot of attempts of auth with the same data
    in the one time period"""

    def __init__(self, message="A lot of attempts to auth."):
        super().__init__(message)


class UserRateLimitingError(RateLimitingError):
    pass


class EmailRateLimitingError(RateLimitingError):
    pass


class NextCodeAttemptNotPassedError(Exception):
    """The error occurs when client ask new code in the time interval
    when new attemnt does't allowed"""

    def __init__(
        self,
        message="Attempt to get new code not allowed yet."
        + " Please wait a bit more",
    ):
        super().__init__(message)


# ===================================== #
#            Article errors             #
# ===================================== #


class TagAlreadyImplementedError(Exception):
    """Occurs when the tag already exists in the article"""

    def __init__(self, message="Tag already implemented in the article."):
        super().__init__(message)


class ArticleAlreadyExistsError(Exception):
    """Occurs when the article already exists in the database"""

    def __init__(self, message="Article already exists in the database."):
        super().__init__(message)


class ArticleDoesNotExistsError(Exception):
    """Occurs when the article doesn't exists in the database"""

    def __init__(self, message="Article doesn't exists in the database."):
        super().__init__(message)


class AuthorDoesNotExistsError(Exception):
    """Occurs when the author doesn't exists in the database"""

    def __init__(self, message="Author doesn't exists in the database."):
        super().__init__(message)


class AuthorIntegrityError(Exception):
    """Occurs when the author data is invalid"""

    def __init__(self, message="Author data is invalid."):
        super().__init__(message)


class ArticleDatabaseError(Exception):
    """Occurs with database error with article data"""

    def __init__(self, message="Article data database error."):
        super().__init__(message)


class SlugAlreadyExistsError(Exception):
    """Occurs when the article or tag with the same slug already exists."""

    def __init__(self, message="The same slug already exists."):
        super().__init__(message)


class TitleAlreadyExistsError(Exception):
    """
    Occurs when the article with the same title and language already exists
    """

    def __init__(
        self, message="The same title already exists in the some article."
    ):
        super().__init__(message)


class TagAlreadyExistsError(Exception):
    """
    Occurs when the tag with the same name and language already exists
    """

    def __init__(self, message="The same tag already exists."):
        super().__init__(message)


class ArticleIntegrityError(Exception):
    """The error occurs when database throw
    IntegrityError after operation with article
    or article_translate data.
    """

    def __init__(self, message="The integrity error of article data."):
        super().__init__(message)


class TagDoesNotExistsError(Exception):
    """The error Occurs when the tag doesn't exists."""

    def __init__(self, message="The tag doesn't exists."):
        super().__init__(message)


class TagIntegrityError(Exception):
    """The error occurs when database throw
    IntegrityError after operation with tag
    or tag_translate data.
    """

    def __init__(self, message="The integrity error of tag data."):
        super().__init__(message)


class TagDatabaseError(Exception):
    pass


class ContentTitleValidationError(Exception):
    """The error occurs when the content of the article is not valid."""

    def __init__(self, message="The title of the article is not valid."):
        super().__init__(message)


class SlugIsMissingError(Exception):
    """The error occurs when the slug of the article is missing"""

    def __init__(self, message="The slug of the article is missing."):
        super().__init__(message)


# ===================================== #
#            Content errors             #
# ===================================== #


class ContentDBError(Exception):
    """The error occurs when database throw
    DatabaseError after operation with content.
    """

    def __init__(self, message="DB error with operation of content"):
        super().__init__(message)


class ContentAlreadyExistsError(Exception):
    def __init__(self, message="Content already exists with this fields."):
        super().__init__(message)


class ContentWithThisTitleAlreadyExistsError(Exception):
    """The error occurs when the content with this title already exists."""

    def __init__(self, message="The content with this title already exists."):
        super().__init__(message)


class ContentIntegrityError(Exception):
    """The error occurs when database throw
    IntegrityError after operation with content
    or content_translate data.
    """

    def __init__(self, message="The integrity error of content data."):
        super().__init__(message)


class ContentDoesNotExistsError(Exception):
    """The error occurs when database return None
    of get content request"""

    def __init__(self, message="The content doesn't exists"):
        super().__init__(message)


# ===================================== #
#             Deal errors               #
# ===================================== #


class DealError(Exception):
    def __init__(self, message="Undefined error with deal"):
        super().__init__(message)


class DealAlreadyExistsError(Exception):
    def __init__(self, message="Deal already exists"):
        super().__init__(message)


class DealLeadNotFoundError(Exception):
    def __init__(self, message="Deal lead not found"):
        super().__init__(message)


class DealManagerNotFoundError(Exception):
    def __init__(self, message="Deal manager not found"):
        super().__init__(message)


class UserNotFoundError(Exception):
    def __init__(self, message="User has'n been founded."):
        super().__init__(message)


class DealSaleStageNotFoundError(Exception):
    def __init__(self, message="Deal sale stage not found"):
        super().__init__(message)


class DealLostReasonNotFoundError(Exception):
    def __init__(self, message="Deal lost reason not found"):
        super().__init__(message)


class DealDBError(Exception):
    def __init__(self, message="Internal server error"):
        super().__init__(message)


class MessageAlreadyExistsError(Exception):
    def __init__(self, message="Message with this id already exists"):
        super().__init__(message)


class DealNotFoundError(Exception):
    def __init__(self, message="The deal has't been founded."):
        super().__init__(message)


class ChatNotActiveError(Exception):
    def __init__(self, message="Chat is not active"):
        super().__init__(message)
