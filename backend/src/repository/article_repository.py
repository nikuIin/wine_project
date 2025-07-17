from pathlib import Path
from uuid import UUID

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from sqlalchemy import delete, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from core.logger.logger import get_configure_logger
from db.models import Article as ArticleModel
from db.models import ArticleTranslate as ArticleTranslateModel
from db.models import Tag as TagModel
from db.models import TagArticle as TagArticleModel
from db.models import TagTranslate as TagTranslateModel
from domain.entities.tag import Tag
from domain.enums import LanguageEnum
from domain.exceptions import (
    ArticleAlreadyExistsError,
    ArticleDatabaseError,
    ArticleDoesNotExistsError,
    ArticleIntegrityError,
    AuthorDoesNotExistsError,
    LanguageDoesNotExistsError,
    SlugAlreadyExistsError,
    TagAlreadyExistsError,
    TagDoesNotExistsError,
    TagIntegrityError,
    TitleAlreadyExistsError,
)
from schemas.article_schema import ArticleCreateSchema, ArticleUpdateSchema

logger = get_configure_logger(Path(__file__).stem)


class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def article_insert(self, article: ArticleCreateSchema):
        article_model = ArticleModel(
            article_id=article.article_id,
            author_id=article.author_id,
            category_id=article.category_id,
            status_id=article.status,
            slug=article.slug,
        )
        article_translate_model = ArticleTranslateModel(
            article_id=article.article_id,
            language_id=article.language,
            title=article.title,
            content=article.content,
            image_src=article.image_src,
        )

        try:
            async with self.__session as session:
                session.add_all([article_model, article_translate_model])
                await session.commit()

        except IntegrityError as error:
            logger.debug(
                "Integrity error when insert article %s",
                article.article_id,
                exc_info=error,
            )
            if isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore  # noqa: SIM102
                if "article_author_id_fkey" in str(error):
                    raise AuthorDoesNotExistsError from error
                elif "article_translate_language_id_fkey" in str(error):
                    raise LanguageDoesNotExistsError from error
            elif isinstance(error.orig.__cause__, UniqueViolationError):  # type: ignore  # noqa: SIM102
                if "article_slug_key" in str(error):
                    raise SlugAlreadyExistsError from error
                elif "article_title_language_unique" in str(error):
                    raise TitleAlreadyExistsError from error
                elif "article_pkey" in str(error):
                    raise ArticleAlreadyExistsError(
                        "Article with this id already exists."
                    ) from error
            raise ArticleIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DB error when insert article: %s", article, exc_info=error
            )
            raise ArticleDatabaseError from error

    async def update_article(  # noqa: C901 # TODO: very complex method
        self,
        article_id: UUID,
        language: LanguageEnum,
        update_article: ArticleUpdateSchema,
    ):
        update_article_stmt = text(
            """
            update article
            set author_id = :author_id,
                slug = :slug,
                category_id = :category_id,
                views_count = :views_count,
                status_id = :status,
                updated_at = current_timestamp
            where article_id = :article_id
            """
        )
        update_article_translate_stmt = text(
            """
            update article_translate
            set title = :title,
                language_id = :language_id,
                content = :content,
                image_src = :image_src
            where article_id = :article_id
            and language_id = :current_language_id
            """
        )

        try:
            async with self.__session as session:
                await session.execute(
                    update_article_stmt,
                    params={
                        "article_id": article_id,
                        "slug": update_article.slug,
                        "author_id": update_article.author_id,
                        "category_id": update_article.category_id,
                        "views_count": update_article.views_count,
                        "status": update_article.status,
                    },
                )
                await session.execute(
                    update_article_translate_stmt,
                    params={
                        "article_id": article_id,
                        "current_language_id": language,
                        "title": update_article.title,
                        "content": update_article.content,
                        "language_id": update_article.language,
                        "image_src": update_article.image_src,
                    },
                )
                await session.commit()

        except IntegrityError as error:
            logger.debug(
                "Integrity error when update article %s to data: %s",
                article_id,
                update_article,
                exc_info=error,
            )
            if isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore  # noqa: SIM102
                if "article_author_id_fkey" in str(error):
                    raise AuthorDoesNotExistsError from error
                elif "article_translate_language_id_fkey" in str(error):
                    raise LanguageDoesNotExistsError from error
            elif isinstance(error.orig.__cause__, UniqueViolationError):  # type: ignore  # noqa: SIM102
                if "article_slug_key" in str(error):
                    raise SlugAlreadyExistsError from error
                elif "article_title_language_unique" in str(error):
                    raise TitleAlreadyExistsError from error
                elif "tag_name_language_unique" in str(error):
                    raise TagAlreadyExistsError from error

        except DBAPIError as error:
            logger.error(
                "DB error when update article %s to data: %s",
                article_id,
                update_article,
                exc_info=error,
            )
            raise ArticleDatabaseError from error

    async def delete_article(self, article_id: UUID):
        delete_article = text(
            """
            delete from article where article_id = :article_id
            """
        )
        delete_translate_article = text(
            """
            delete from article_translate where article_id = :article_id
            """
        )

        try:
            async with self.__session as session:
                translate_article_delete = await session.execute(
                    delete_translate_article,
                    params={"article_id": article_id},
                )
                article_delete = await session.execute(
                    delete_article,
                    params={
                        "article_id": article_id,
                    },
                )
                await session.commit()

            return article_delete.rowcount + translate_article_delete.rowcount  # type: ignore
        except DBAPIError as error:
            logger.error(
                "Error when trying to delete article %s",
                article_id,
                exc_info=error,
            )
            raise ArticleDatabaseError from error

    async def add_tag(self, tag: Tag) -> None:
        tag_model = TagModel(
            tag_id=tag.tag_id,
        )
        tag_translate_model = TagTranslateModel(
            tag_id=tag.tag_id,
            language_id=tag.language,
            name=tag.name,
        )

        try:
            async with self.__session as session:
                session.add_all([tag_model, tag_translate_model])
                await session.commit()

        except IntegrityError as error:
            logger.debug(
                "Integrity error when add tag %s",
                tag,
                exc_info=error,
            )
            if isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore  # noqa: SIM102
                if "article_author_id_fkey" in str(error):
                    raise AuthorDoesNotExistsError from error
                elif "article_translate_language_id_fkey" in str(error):
                    raise LanguageDoesNotExistsError from error
            elif isinstance(error.orig.__cause__, UniqueViolationError):  # type: ignore  # noqa: SIM102
                if "tag_name_language_unique" in str(
                    error
                ) or "tag_pkey" in str(error):
                    raise TagAlreadyExistsError from error
                elif "tag_slug_key" in str(error):
                    raise SlugAlreadyExistsError from error
                elif "article_title_language_unique" in str(error):
                    raise TitleAlreadyExistsError from error
            logger.warning(
                "Doesn't deretmined error while adding tag %s",
                tag,
                exc_info=error,
            )
            raise TagIntegrityError from error

        except DBAPIError as error:
            logger.error("DB error when add tag: %s", tag, exc_info=error)
            raise ArticleDatabaseError from error

    async def delete_tag(self, tag_id: int) -> None:
        delete_tag = delete(TagModel).where(TagModel.tag_id == tag_id)
        delete_tag_translate = delete(TagTranslateModel).where(
            TagTranslateModel.tag_id == tag_id
        )

        try:
            async with self.__session as session:
                await session.execute(delete_tag)
                await session.execute(delete_tag_translate)
                await session.commit()
        except DBAPIError as error:
            logger.error(
                "DB error when delete tag: %s", tag_id, exc_info=error
            )
            raise ArticleDatabaseError from error

    async def get_tags(
        self, article_id: UUID, language: LanguageEnum
    ) -> list[Tag]:
        # we dont use limit/offest because the tags quantity
        # in the one article is limited.
        stmt = text(
            """
            select
                tag_id,
                name,
                language_id as language
            from tag_article ta
            join tag_translate using(tag_id)
            where article_id = :article_id
            and language_id = :language_id
            """
        )
        try:
            async with self.__session as session:
                tags = await session.execute(stmt)
            tags = tags.mappings().fetchall()
            if not tags:
                logger.warning(
                    "No tags found for article_id %s and language %s",
                    article_id,
                    language,
                )
                return []
            return [Tag.model_validate(tag) for tag in tags]

        except DBAPIError as error:
            logger.error(
                "DB error when get tags: %s", article_id, exc_info=error
            )
            raise ArticleDatabaseError from error

    # TODO: change domain model Tag to some list tag-schema
    async def set_tags_to_article(
        self, article_id: UUID, tags: list[Tag]
    ) -> None:
        models = [
            TagArticleModel(tag_id=tag.tag_id, article_id=article_id)
            for tag in tags
        ]

        try:
            async with self.__session as session:
                session.add_all(models)
                await session.commit()
        except IntegrityError as error:
            logger.debug(
                "Integrity error when add tags %s to article %s",
                tags,
                article_id,
                exc_info=error,
            )
            if isinstance(error.orig.__cause__, ForeignKeyViolationError):  # type: ignore  # noqa: SIM102
                if "tag_article_tag_id_fkey" in str(error):
                    raise ArticleDoesNotExistsError(
                        "Article or tag doesn't exists."
                    ) from error
            elif isinstance(error.orig.__cause__, UniqueViolationError):  # type: ignore  # noqa: SIM102
                raise TagAlreadyExistsError from error
            logger.warning(
                "Doesn't determined integration error when"
                + " adding %s tags to article %s",
                tags,
                article_id,
                exc_info=error,
            )
            raise ArticleIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DB error when add tags %s to article %s",
                tags,
                article_id,
                exc_info=error,
            )
            raise ArticleDatabaseError from error
