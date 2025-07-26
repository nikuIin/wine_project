import base64
import zlib
from pathlib import Path
from re import search
from string import ascii_letters, digits
from uuid import UUID

from fastapi import Depends
from sqlalchemy.exc import DBAPIError
from uuid_extensions import uuid7

from core.general_constants import DEFAULT_LIMIT, RUSSIAN_LOWERCASE_LETTERS
from core.logger.logger import get_configure_logger
from domain.entities.article import Article, ArticleCategory, Author
from domain.entities.tag import Tag
from domain.enums import (
    ArticleCategoriesID,
    ArticleSortBy,
    ArticleStatus,
    LanguageEnum,
    SortOrder,
    TSQUERYRules,
)
from domain.exceptions import (
    ArticleAlreadyExistsError,
    ArticleDatabaseError,
    ArticleDoesNotExistsError,
    ArticleIntegrityError,
    AuthorDoesNotExistsError,
    AuthorIntegrityError,
    LanguageDoesNotExistsError,
    SlugAlreadyExistsError,
    SlugIsMissingError,
    TagAlreadyExistsError,
    TagDatabaseError,
    TagDoesNotExistsError,
    TagIntegrityError,
    TitleAlreadyExistsError,
)
from repository.article_repository import (
    ArticleRepository,
    article_repository_dependency,
)
from schemas.article_schema import (
    ArticleCategorySchema,
    ArticleCreateSchema,
    ArticleListSchema,
    ArticleResponseSchema,
    ArticleShortSchema,
    ArticleTranslateCreateSchema,
    ArticleTranslateUpdateSchema,
    ArticleUpdateSchema,
    AuthorShortSchema,
    TagCreateSchema,
    TagGetSchema,
    TagIDRequest,
    TagSchema,
    TagTranslateCreateSchema,
    TagTranslateUpdateSchema,
)

logger = get_configure_logger(Path(__file__).stem)


class ArticleService:
    def __init__(self, article_repository: ArticleRepository):
        self.__article_repository = article_repository

    async def add_article(self, article_create: ArticleCreateSchema) -> None:
        try:
            # initialize article
            article = Article(
                article_id=article_create.article_id
                if article_create.article_id
                else uuid7(),
                category=ArticleCategory(
                    category_id=article_create.category_id
                )
                if article_create.category_id
                else None,
                image_src=article_create.image_src,
                views_count=article_create.views_count,
                title=article_create.title,
                content=article_create.content,
                language=article_create.language,
                status=article_create.status,
                author=Author(author_id=article_create.author_id),
                slug=article_create.slug,
                tags=[Tag(tag_id=tag_id) for tag_id in article_create.tags]
                if article_create.tags
                else [],
            )

            # save in the database
            await self.__article_repository.article_insert(article)

        except ArticleIntegrityError as error:
            raise error
        except AuthorDoesNotExistsError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except SlugAlreadyExistsError as error:
            raise error
        except TitleAlreadyExistsError as error:
            raise error
        except ArticleAlreadyExistsError as error:
            raise error
        except ArticleDatabaseError as error:
            raise error

    async def add_translate_to_article(
        self,
        article_id: UUID,
        language: LanguageEnum,
        article_translate: ArticleTranslateCreateSchema,
    ):
        try:
            await self.__article_repository.insert_article_translate(
                article_id=article_id,
                language=language,
                article_translate=article_translate,
            )
        except AuthorDoesNotExistsError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except SlugAlreadyExistsError as error:
            raise error
        except TitleAlreadyExistsError as error:
            raise error
        except ArticleAlreadyExistsError as error:
            raise error
        except ArticleDatabaseError as error:
            raise error

    async def update_translate_article(
        self,
        article_id: UUID,
        language: LanguageEnum,
        article_translate: ArticleTranslateUpdateSchema,
    ):
        try:
            await self.__article_repository.update_article_translate(
                article_id=article_id,
                language=language,
                article_translate=article_translate,
            )
        except AuthorDoesNotExistsError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except SlugAlreadyExistsError as error:
            raise error
        except TitleAlreadyExistsError as error:
            raise error
        except ArticleAlreadyExistsError as error:
            raise error
        except ArticleDatabaseError as error:
            raise error

    def validate_article(self, article: Article | None) -> bool:
        if not article:
            raise ArticleDoesNotExistsError(
                "Article is None. Check the article ID or language."
            )
        if not article.author:
            raise AuthorDoesNotExistsError("The article must have an author.")

        return True

    def _get_author_validate_data(self, article: Article) -> AuthorShortSchema:
        """Validate the presence of an author and transform data into a DTO.

        Ensure that an article has an associated author before attempting
        to access author data, preventing potential runtime errors.

        Args:
            article: The Article domain entity.

        Raises:
            AuthorDoesNotExistsError: If the article does not have an
                author.

        Returns:
            An AuthorShortSchema with essential, client-safe author data.
        """
        if not article.author:
            raise AuthorDoesNotExistsError("Article does not have an author")
        elif (
            not article.author.author_id
            or not article.author.first_name
            or not article.author.last_name
        ):
            raise AuthorIntegrityError("Author data is invalid")

        return AuthorShortSchema(
            author_id=article.author.author_id,
            first_name=article.author.first_name,
            last_name=article.author.last_name,
            middle_name=article.author.middle_name,
            avatar=article.author.avatar,
        )

    async def get_article(
        self, article_id: UUID, language: LanguageEnum
    ) -> ArticleResponseSchema | None:
        """Retrieve, process, and format a single article for a client.

        Orchestrate fetching an article, converting it to HTML,
        generating a table of contents, validating associated data, and
        packaging it into a response schema.

        Args:
            article_id: The unique identifier for the article.
            language: The language in which to retrieve the article.

        Returns:
            An ArticleResponseSchema object if the article is found and
            valid, otherwise None.

        Raises:
            ArticleDatabaseError: If a database-level error occurs.
            ArticleIntegrityError: If the article is missing critical
                data (e.g. slug).
            AuthorDoesNotExistsError: If the article does not have an
                author.
        """
        try:
            article = await self.__article_repository.get_article(
                article_id, language
            )

            if article:
                # A slug is crucial for SEO-friendly URLs. Its absence
                # indicates a data integrity issue.
                if not article.slug:
                    raise SlugIsMissingError("Slug is missing")

                # Compress the article content.
                compressed_content = (
                    self._compress_string(article.content)
                    if article.content
                    else ""
                )

                # Validate that the article has a valid author and get
                # their data.
                author = self._get_author_validate_data(article=article)

                return ArticleResponseSchema(
                    title=article.title,
                    slug=article.slug,
                    image_src=article.image_src,
                    content=compressed_content,
                    category=ArticleCategorySchema(
                        **article.category.model_dump()
                    )
                    if article.category
                    else None,
                    views_count=article.views_count,
                    tags=[
                        TagSchema(**tag.model_dump()) for tag in article.tags
                    ],
                    status=article.status,
                    author=author,
                    language=article.language,
                )
            else:
                raise ArticleDoesNotExistsError(
                    f"Article with id {article_id} and language {language}"
                    + " does not exists"
                )

        except ArticleIntegrityError as error:
            raise error
        except AuthorDoesNotExistsError as error:
            raise error
        except ArticleDatabaseError as error:
            raise error

    def _get_seached_words(self, input_text: str) -> set[str]:
        """Prepare text to ts_query method with AND rule.

        Examples:
            "my cute string" -> "set(my, cute, string)"
        Args:
            search_text (str): The text to be prepared for ts_query search.
        Returns:
            set: The set of searched words without specified symbols
                 and mutiply spaces.
        """
        input_text = "".join(
            char.lower()
            if char.lower()
            in set(ascii_letters + digits) | RUSSIAN_LOWERCASE_LETTERS
            else " "
            for char in input_text
        )
        return set(input_text.split())

    def _text_preparation_to_tsquery(
        self,
        input_text: str,
        rule: TSQUERYRules = TSQUERYRules.AND,
        excluded: bool = False,
    ):
        """Prepare text to ts_query method with specified rule.

        Args:
            input_text (str): The text to be prepared for ts_query search.
            rule (TSQUERYRules): The rule to be used for ts_query search.
            excluded (bool): Is words from input_text exclude from searching
                            or include. Default include (=False).
        Returns:
            str: The prepared text for ts_query search.
        """
        searched_words = self._get_seached_words(input_text=input_text)

        if excluded:
            searched_words = {"!" + word for word in searched_words}

        return f" {rule} ".join(searched_words)

    def _compress_string(self, input_string: str) -> str:
        compressed = zlib.compress(input_string.encode("utf-8"), wbits=-15)
        encoded = base64.b64encode(compressed).decode("utf-8")
        return encoded

    async def get_articles(
        self,
        # filters params
        language: LanguageEnum,
        category_id: tuple[ArticleCategoriesID, ...] | None = None,
        statuses: tuple[ArticleStatus, ...] | None = None,
        tags: tuple[int, ...] | None = None,
        searched_text: str | None = None,
        # pagination params
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        order_by: ArticleSortBy = ArticleSortBy.PUBLISHED_AT,
        order_direction: SortOrder = SortOrder.DESC,
    ):
        """Retrieve a paginated and filtered list of articles.

        Fetch articles from the repository based on specified
        filtering, sorting, and pagination parameters.

        Args:
            language: The language of the articles to retrieve.
            category_id: A tuple of category IDs to filter by.
            statuses: A tuple of article statuses to filter by.
            tags: A tuple of tag IDs to filter by.
            limit: The maximum number of articles to return.
            offset: The number of articles to skip for pagination.
            order_by: The field by which to sort the articles.
            order_direction: The direction of the sorting (asc or desc).

        Raises:
            ArticleIntegrityError: If an integrity error occurs.
            DBAPIError: If a generic database error occurs.

        Returns:
            A list of articles matching the criteria.
        """
        try:
            if searched_text:
                searched_text = self._text_preparation_to_tsquery(
                    searched_text
                )

            articles = await self.__article_repository.get_articles(
                language=language,
                category_id=category_id,
                statuses=statuses,
                tags=tags,
                ts_query_of_searched_words=searched_text
                if searched_text
                else None,
                limit=limit,
                offset=offset,
                order_by=order_by,
                order_direction=order_direction,
            )

            return ArticleListSchema(
                language=language,
                articles=[
                    ArticleShortSchema(**article.model_dump(exclude_none=True))
                    for article in articles
                ],
            )

        except ArticleIntegrityError as error:
            raise error
        except DBAPIError as error:
            raise error

    async def update_article(
        self,
        article_id: UUID,
        language: LanguageEnum,
        article_update: ArticleUpdateSchema,
    ) -> int:
        try:
            # initialize article
            article = Article(
                article_id=article_id,
                category=ArticleCategory(
                    category_id=article_update.category_id
                )
                if article_update.category_id
                else None,
                views_count=article_update.views_count,
                title=article_update.title,
                image_src=article_update.image_src,
                content=article_update.content,
                language=article_update.language,
                author=Author(author_id=article_update.author_id),
                slug=article_update.slug,
                tags=[
                    Tag(tag_id=tag.tag_id, name=tag.name)
                    for tag in article_update.tags
                ]
                if article_update.tags
                else [],
            )

            return await self.__article_repository.update_article(
                article_id=article_id,
                update_article=article,
                language=language,
            )
        except AuthorIntegrityError as error:
            raise error
        except AuthorDoesNotExistsError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except TitleAlreadyExistsError as error:
            raise error
        except TagAlreadyExistsError as error:
            raise error
        except SlugAlreadyExistsError as error:
            raise error
        except ArticleIntegrityError as error:
            raise error
        except ArticleDatabaseError as error:
            raise error

    async def delete_article(
        self,
        article_id: UUID,
    ) -> int:
        try:
            return await self.__article_repository.delete_article(
                article_id=article_id,
            )
        except ArticleDatabaseError as error:
            raise error

    async def delete_translate_from_article(
        self, article_id: UUID, language: LanguageEnum
    ):
        try:
            return await self.__article_repository.delete_translate_article(
                article_id=article_id, language=language
            )
        except ArticleDatabaseError as error:
            raise error

    async def get_recommendations(self, article: Article) -> list[Article]: ...

    async def create_tag(self, tag: TagCreateSchema) -> None:
        try:
            await self.__article_repository.create_tag(tag)
        except TagAlreadyExistsError as error:
            raise error
        except TagDoesNotExistsError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except SlugAlreadyExistsError as error:
            raise error
        except TitleAlreadyExistsError as error:
            raise error
        except TagIntegrityError as error:
            raise error
        except TagDatabaseError as error:
            raise error

    async def create_translate_to_tag(
        self,
        tag_id: int,
        language: LanguageEnum,
        tag_translate: TagTranslateCreateSchema,
    ):
        try:
            await self.__article_repository.create_translate_to_tag(
                tag_id=tag_id,
                language=language,
                tag_translate=tag_translate,
            )
        except LanguageDoesNotExistsError as error:
            raise error
        except TagDoesNotExistsError as error:
            raise error
        except TagAlreadyExistsError as error:
            raise error
        except TagIntegrityError as error:
            raise error
        except TagDatabaseError as error:
            raise error

    async def update_translate_of_tag(
        self,
        tag_id: int,
        language: LanguageEnum,
        tag_translate: TagTranslateUpdateSchema,
    ):
        try:
            await self.__article_repository.update_tag_translate(
                tag_id=tag_id,
                language=language,
                tag_translate=tag_translate,
            )
        except LanguageDoesNotExistsError as error:
            raise error
        except TagDoesNotExistsError as error:
            raise error
        except TagAlreadyExistsError as error:
            raise error
        except TagIntegrityError as error:
            raise error
        except TagDatabaseError as error:
            raise error

    async def delete_tag(
        self,
        tag_id: int,
    ) -> None:
        try:
            await self.__article_repository.delete_tag(tag_id)
        except TagDoesNotExistsError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except TagIntegrityError as error:
            raise error
        except TagDatabaseError as error:
            raise error

    async def set_tags_to_article(self, article_id: UUID, tags: list[int]):
        try:
            domain_tags_list = [Tag(tag_id=tag_id) for tag_id in tags]
            await self.__article_repository.set_tags_to_article(
                article_id=article_id,
                tags=domain_tags_list,
            )
        except ArticleDoesNotExistsError as error:
            raise error
        except TagAlreadyExistsError as error:
            raise error
        except ArticleIntegrityError as error:
            raise error
        except ArticleDatabaseError as error:
            raise error


def article_service_dependency(
    article_repository: ArticleRepository = Depends(
        article_repository_dependency
    ),
):
    return ArticleService(article_repository)
