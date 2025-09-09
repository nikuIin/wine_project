from pathlib import Path
from uuid import UUID

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from fastapi import Depends
from sqlalchemy import (
    and_,
    cast,
    delete,
    func,
    select,
    text,
    update,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql.ext import to_tsquery
from sqlalchemy.dialects.postgresql.types import REGCONFIG
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from core.general_constants import DEFAULT_LIMIT
from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import Article as ArticleModel
from db.models import ArticleTranslate as ArticleTranslateModel
from db.models import BlogCategoryTranslate as BlogCategoryTranslateModel
from db.models import Language as LanguageModel
from db.models import Tag as TagModel
from db.models import TagArticle as TagArticleModel
from db.models import TagTranslate as TagTranslateModel
from domain.entities.article import Article, ArticleCategory, Author
from domain.entities.tag import Tag
from domain.enums import (
    ArticleCategoriesID,
    ArticleSortBy,
    ArticleStatus,
    LanguageEnum,
    SortOrder,
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
    TagAlreadyExistsError,
    TagDatabaseError,
    TagDoesNotExistsError,
    TagIntegrityError,
    TitleAlreadyExistsError,
)
from schemas.article_schema import (
    ArticleCreateSchema,
    ArticleTranslateCreateSchema,
    ArticleTranslateUpdateSchema,
    ArticleUpdateSchema,
    TagCreateSchema,
    TagGetSchema,
    TagTranslateCreateSchema,
    TagTranslateUpdateSchema,
)

logger = get_configure_logger(Path(__file__).stem)


# Aliases
A = ArticleModel.__table__.alias("a")
AT = ArticleTranslateModel.__table__.alias("at")
L = LanguageModel.__table__.alias("l")
TA = TagArticleModel.__table__.alias("ta")
BCT = BlogCategoryTranslateModel.__table__.alias("bc")
TT = TagTranslateModel.__table__.alias("tt")


class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def update_views(self, article_id: UUID) -> int:
        stmt = text(
            """
            update article
            set views_count = views_count + 1
            where article_id = :article_id
            """
        )

        try:
            async with self.__session as session:
                result = await session.execute(
                    stmt, {"article_id": article_id}
                )
                await session.commit()

            return result.rowcount  # type: ignore

        except DBAPIError as error:
            logger.error(
                "DB error when update views of article %s",
                article_id,
                exc_info=error,
            )
            raise ArticleDatabaseError from error

    async def get_article(
        self, article_id: UUID, language: LanguageEnum
    ) -> Article | None:
        stmt = text(
            """
            select
                a.article_id,
                a.author_id,
                mu.first_name as author_first_name,
                mu.last_name as author_last_name,
                mu.middle_name as author_middle_name,
                mu.profile_picture_link as author_avatar,
                a.views_count,
                a.slug,
                bct.blog_category_id as category_id,
                bct.name as category_name,
                at.title,
                at.language_id,
                at.content,
                at.image_src as article_image,
                a.published_at,
                a.status_id,
                nullif(
                    jsonb_agg(
                        jsonb_build_object(
                            'tag_id', tt.tag_id,
                            'tag_name', tt.name
                        )
                    ), '[{"tag_id": null, "tag_name": null}]'::jsonb
                ) as tags
            from article a
            join article_translate at using(article_id)
            join author athr on athr.user_id = a.author_id
            join md_user mu using(user_id)
            left join blog_category_translate bct on (
                a.blog_category_id = bct.blog_category_id
                and bct.language_id = at.language_id
            )
            left join tag_article ta using(article_id)
            left join tag_translate tt on (
                    tt.tag_id = ta.tag_id
                    and tt.language_id = at.language_id
                )
            where at.language_id = :language_id
                  and a.article_id = :article_id
            group by
                a.article_id,
                mu.user_id,
                at.language_id,
                at.article_id,
                bct.blog_category_id,
                bct.language_id;
            """
        )

        try:
            async with self.__session as session:
                result = await session.execute(
                    stmt,
                    {
                        "language_id": language,
                        "article_id": article_id,
                    },
                )
                article = result.mappings().fetchone()
                logger.debug("Article with id %s: %s", article_id, article)
                if article:
                    tags = []
                    if article["tags"]:
                        logger.debug(
                            "Tags of article %s: %s",
                            article_id,
                            article["tags"],
                        )
                        tags = [
                            Tag(tag_id=tag["tag_id"], name=tag["tag_name"])
                            for tag in article["tags"]
                            if article["tags"] and tag["tag_id"]
                        ]

                    author = Author(
                        author_id=article["author_id"],
                        first_name=article["author_first_name"],
                        last_name=article["author_last_name"],
                        middle_name=article["author_middle_name"],
                        avatar=article["author_avatar"],
                    )

                    article = Article(
                        article_id=article["article_id"],
                        title=article["title"],
                        language=article["language_id"],
                        category=ArticleCategory(
                            category_id=article["category_id"],
                            name=article["category_name"],
                        )
                        if article["category_id"]
                        else None,
                        image_src=article["article_image"],
                        content=article["content"],
                        views_count=article["views_count"],
                        slug=article["slug"],
                        author=author,
                        tags=tags,
                        status=article["status_id"],
                        published_at=article["published_at"],
                    )
                    return article
                return None

        except DBAPIError as error:
            logger.error(
                "DB error when get article: %s", article_id, exc_info=error
            )
            raise ArticleDatabaseError from error

    async def article_insert(self, article: Article):
        article_model = ArticleModel(
            article_id=article.article_id,
            author_id=article.author.author_id if article.author else None,
            views_count=article.views_count,
            blog_category_id=article.category.category_id
            if article.category
            else None,
            status_id=article.status,
            published_at=article.published_at,
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

    async def insert_article_translate(
        self,
        article_id: UUID,
        language: LanguageEnum,
        article_translate: ArticleTranslateCreateSchema,
    ):
        article_translate_model = ArticleTranslateModel(
            article_id=article_id,
            language_id=language,
            image_src=article_translate.image_src,
            title=article_translate.title,
            content=article_translate.content,
        )

        try:
            async with self.__session as session:
                session.add(article_translate_model)
                await session.commit()

            logger.info(
                "The translate in %s to article %s has been"
                + " successfully added",
                language,
                article_id,
            )

        except IntegrityError as error:
            if "article_translate_article_id_fkey" in str(error):
                raise ArticleDoesNotExistsError(
                    "Article with this id does't exist."
                ) from error
            elif "article_translate_language_id_fkey" in str(error):
                raise LanguageDoesNotExistsError(
                    "This language does't exists."
                ) from error
            elif "article_translate_language_id_fkey" in str(error):
                raise ArticleAlreadyExistsError(
                    f"Language {language} doesn't exists."
                ) from error
            elif "article_translate_pkey" in str(error):
                raise ArticleAlreadyExistsError(
                    "Article with this id and language already exists."
                ) from error
            elif "article_title_language_unique" in str(error):
                raise TitleAlreadyExistsError(
                    f"Title on language {language} already exists."
                ) from error

            raise ArticleIntegrityError from error

    async def update_article_translate(
        self,
        article_id: UUID,
        language: LanguageEnum,
        article_translate: ArticleTranslateUpdateSchema,
    ):
        stmt = (
            update(ArticleTranslateModel)
            .where(
                and_(
                    ArticleTranslateModel.article_id == article_id,
                    ArticleTranslateModel.language_id == language,
                )
            )
            .values(
                article_id=article_translate.article_id,
                language_id=article_translate.language,
                image_src=article_translate.image_src,
                title=article_translate.title,
                content=article_translate.content,
            )
        )

        try:
            async with self.__session as session:
                await session.execute(stmt)
                await session.commit()

            logger.info(
                "The translate in %s to article %s has been"
                + " successfully added",
                language,
                article_id,
            )

        except IntegrityError as error:
            if "article_translate_article_id_fkey" in str(error):
                raise ArticleDoesNotExistsError(
                    "Article with this id does't exist."
                ) from error
            elif "article_translate_language_id_fkey" in str(error):
                raise LanguageDoesNotExistsError(
                    "This language does't exists."
                ) from error
            elif "article_translate_language_id_fkey" in str(error):
                raise ArticleAlreadyExistsError(
                    f"Language {language} doesn't exists."
                ) from error
            elif "article_translate_pkey" in str(error):
                raise ArticleAlreadyExistsError(
                    "Article with this id and language already exists."
                ) from error
            elif "article_title_language_unique" in str(error):
                raise TitleAlreadyExistsError(
                    f"Title on language {language} already exists."
                ) from error

            raise ArticleIntegrityError from error

    async def get_articles(
        self,
        # filters params
        language: LanguageEnum,
        category_id: tuple[ArticleCategoriesID, ...] | None = None,
        statuses: tuple[ArticleStatus, ...] | None = None,
        tags: tuple[int, ...] | None = None,
        ts_query_of_searched_words: str | None = None,
        # pagination params
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        order_by: ArticleSortBy = ArticleSortBy.PUBLISHED_AT,
        order_direction: SortOrder = SortOrder.DESC,
    ) -> list[Article]:
        stmt = (
            select(
                A.c.article_id,
                AT.c.title,
                A.c.views_count,
                A.c.slug,
                A.c.status_id.label("status"),
                L.c.language_id.label("language"),
                BCT.c.blog_category_id,
                BCT.c.name.label("blog_category_name"),
                AT.c.image_src,
                A.c.published_at,
                func.nullif(
                    func.jsonb_agg(
                        func.jsonb_build_object(
                            "tag_id", TT.c.tag_id, "tag_name", TT.c.name
                        )
                    ),
                    cast("[null]", JSONB),
                ).label("tags"),
            )
            .select_from(
                A.join(AT, A.c.article_id == AT.c.article_id)
                .join(L, AT.c.language_id == L.c.language_id)
                .outerjoin(
                    BCT,
                    and_(
                        A.c.blog_category_id == BCT.c.blog_category_id,
                        L.c.language_id == BCT.c.language_id,
                    ),
                )
                .outerjoin(TA, A.c.article_id == TA.c.article_id)
                .outerjoin(
                    TT,
                    and_(
                        TT.c.language_id == L.c.language_id,
                        TT.c.tag_id == TA.c.tag_id,
                    ),
                )
            )
            .where(L.c.language_id == language)
            .group_by(
                A.c.article_id,
                AT.c.language_id,
                AT.c.article_id,
                L.c.language_id,
                BCT.c.language_id,
                BCT.c.blog_category_id,
            )
            .limit(limit)
            .offset(offset)
        )

        # ====== ====== ====== ====== ====== ====== ====== ====== ======
        # dynamic sql editing

        # 1. filtration
        if category_id:
            stmt = stmt.where(A.c.blog_category_id.in_(category_id))
        if statuses:
            stmt = stmt.where(A.c.status_id.in_(statuses))
        if tags:
            stmt = stmt.where(TT.c.tag_id.in_(tags))
        if ts_query_of_searched_words:
            ts_query = to_tsquery(
                L.c.cfgname.cast(REGCONFIG), ts_query_of_searched_words
            )
            stmt = stmt.where(AT.c.tsv_content.op("@@")(ts_query))
            # set order by by weight of ts_vector (title - A, content - B)
            stmt = stmt.order_by(
                func.ts_rank(AT.c.tsv_content, ts_query).desc()
            )
        # 2. order by
        match order_by:
            case ArticleSortBy.VIEWS_COUNT:
                stmt = (
                    stmt.order_by(A.c.views_count.desc())
                    if order_direction == SortOrder.DESC
                    else stmt.order_by(A.c.views_count.asc())
                )
            case ArticleSortBy.PUBLISHED_AT:
                stmt = (
                    stmt.order_by(A.c.published_at.desc().nullsfirst())
                    if order_direction == SortOrder.DESC
                    else stmt.order_by(A.c.published_at.asc())
                )
        # ====== ====== ====== ====== ====== ====== ====== ====== ======

        try:
            async with self.__session as session:
                result = await session.execute(stmt)

            result = result.mappings().all()
            article_list = [
                Article(
                    article_id=article.article_id,
                    language=article.language,
                    title=article.title,
                    slug=article.slug,
                    status=article.status,
                    image_src=article.image_src,
                    views_count=article.views_count,
                    category=ArticleCategory(
                        category_id=article.blog_category_id,
                        name=article.blog_category_name,
                    )
                    if article.blog_category_id
                    else None,
                    published_at=article.published_at,
                    tags=[
                        Tag(
                            tag_id=tag["tag_id"],
                            name=tag["tag_name"],
                        )
                        for tag in article.tags
                        if tag and tag.get("tag_id")
                    ],
                )
                for article in result
            ]

            return article_list

        except IntegrityError as error:
            logger.error(
                "Integrity error of get article list with"
                + " (language, category, statuses_list, tags, limit, offset)"
                + " = (%s, %s, %s, %s, %s, %s)",
                language,
                category_id,
                statuses,
                tags,
                limit,
                offset,
                exc_info=error,
            )
            raise ArticleIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DBAPI error of get article list with"
                + " (language, category, statuses_list, tags, limit, offset)"
                + " = (%s, %s, %s, %s, %s, %s)",
                language,
                category_id,
                statuses,
                tags,
                limit,
                offset,
                exc_info=error,
            )
            raise ArticleDatabaseError from error

    async def update_article(  # noqa: C901 # TODO: very complex method
        self,
        article_id: UUID,
        language: LanguageEnum,
        update_article: Article,
    ) -> int:
        update_article_stmt = text(
            """
            update article
            set author_id = :author_id,
                slug = :slug,
                blog_category_id = :category_id,
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

        if not update_article.author:
            raise AuthorIntegrityError

        try:
            async with self.__session as session:
                result_article = await session.execute(
                    update_article_stmt,
                    params={
                        "article_id": article_id,
                        "slug": update_article.slug,
                        "author_id": update_article.author.author_id,
                        "category_id": update_article.category.category_id
                        if update_article.category
                        else None,
                        "views_count": update_article.views_count,
                        "status": update_article.status,
                    },
                )
                result_article_translate = await session.execute(
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

            return result_article.rowcount + result_article_translate.rowcount  # type: ignore

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

            raise ArticleIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DB error when update article %s to data: %s",
                article_id,
                update_article,
                exc_info=error,
            )
            raise ArticleDatabaseError from error

    async def delete_article(
        self,
        article_id: UUID,
    ) -> int:
        delete_article = delete(ArticleModel).where(
            ArticleModel.article_id == article_id
        )
        delete_translate_article = delete(ArticleTranslateModel).where(
            ArticleTranslateModel.article_id == article_id
        )

        try:
            async with self.__session as session:
                translate_article_delete = await session.execute(
                    delete_translate_article
                )
                article_delete = await session.execute(
                    delete_article,
                )
                await session.commit()

            logger.info(
                "Article with id %s has been deleted",
                article_id,
            )

            return article_delete.rowcount + translate_article_delete.rowcount  # type: ignore

        except DBAPIError as error:
            logger.error(
                "Error when trying to delete article %s",
                article_id,
                exc_info=error,
            )
            raise ArticleDatabaseError from error

    async def delete_translate_article(
        self, article_id: UUID, language: LanguageEnum
    ) -> int:
        delete_translate_article = delete(ArticleTranslateModel).where(
            and_(
                ArticleTranslateModel.article_id == article_id,
                ArticleTranslateModel.language_id == language,
            )
        )

        try:
            async with self.__session as session:
                translate_article_delete = await session.execute(
                    delete_translate_article
                )
                await session.commit()

            logger.info(
                "Article with language %s has been deleted",
                language,
            )

            return translate_article_delete.rowcount  # type: ignore

        except DBAPIError as error:
            logger.error(
                "Error when trying to delete article %s",
                article_id,
                exc_info=error,
            )
            raise ArticleDatabaseError from error

    async def create_tag(self, tag: TagCreateSchema) -> None:
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
                logger.error("Tag doesn't created", exc_info=error)
                if "tag_translate_tag_id_fkey" in str(error):
                    raise TagDoesNotExistsError from error
                elif "tag_translate_language_id_fkey" in str(error):
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
            raise TagDatabaseError from error

    async def create_translate_to_tag(
        self,
        tag_id: int,
        language: LanguageEnum,
        tag_translate: TagTranslateCreateSchema,
    ):
        tag_translate_model = TagTranslateModel(
            tag_id=tag_id,
            language_id=language,
            name=tag_translate.name,
        )

        try:
            async with self.__session as session:
                session.add(tag_translate_model)
                await session.commit()

        except IntegrityError as error:
            if "tag_translate_language_id_fkey" in str(error):
                raise LanguageDoesNotExistsError(
                    f"The language {language} doesn't exists."
                ) from error

            elif "tag_translate_tag_id_fkey" in str(error):
                raise TagDoesNotExistsError(
                    f"The tag with id {tag_id} doesn't exists."
                ) from error

            elif "tag_name_language_unique" in str(error):
                raise TagAlreadyExistsError(
                    f"The tag with {tag_translate.name}"
                    + " in {language} already exists."
                ) from error

            elif "tag_translate_pkey" in str(error):
                raise TagAlreadyExistsError(
                    f"The tag with key {tag_id}-{language} already exists."
                ) from error

            logger.error(
                "Unprocessed integrity error when add translate"
                + " tag with id %s in english %s",
                tag_id,
                language,
                exc_info=error,
            )

            raise TagIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DB error when add translate"
                + " tag with id %s in english %s",
                tag_id,
                language,
                exc_info=error,
            )
            raise TagDatabaseError from error

    async def update_tag_translate(
        self,
        tag_id: int,
        language: LanguageEnum,
        tag_translate: TagTranslateUpdateSchema,
    ):
        stmt = (
            update(TagTranslateModel)
            .where(
                and_(
                    TagTranslateModel.language_id == language,
                    TagTranslateModel.tag_id == tag_id,
                )
            )
            .values(
                name=tag_translate.name,
                language_id=tag_translate.language,
            )
        )
        logger.debug(
            "Update tag with id %s and language %s to %s",
            tag_id,
            language,
            tag_translate,
        )
        try:
            async with self.__session as session:
                await session.execute(stmt)
                await session.commit()

        except IntegrityError as error:
            if "tag_translate_language_id_fkey" in str(error):
                raise LanguageDoesNotExistsError(
                    f"The language {language} doesn't exists."
                ) from error

            elif "tag_translate_tag_id_fkey" in str(error):
                raise TagDoesNotExistsError(
                    f"The tag with id {tag_id} doesn't exists."
                ) from error

            elif "tag_name_language_unique" in str(error):
                raise TagAlreadyExistsError(
                    f"The tag with {tag_translate.name}"
                    + f" in {language} already exists."
                ) from error

            elif "tag_translate_pkey" in str(error):
                raise TagAlreadyExistsError(
                    "The tag with key"
                    + f" {tag_id}-{tag_translate.language}"
                    + " already exists."
                ) from error

            logger.error(
                "Unprocessed integrity error when update translate of"
                + " tag with id %s in english %s",
                tag_id,
                language,
                exc_info=error,
            )

            raise TagIntegrityError from error

        except DBAPIError as error:
            logger.error(
                "DB error when update translate of"
                + " tag with id %s in english %s",
                tag_id,
                language,
                exc_info=error,
            )
            raise TagDatabaseError from error

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

    async def get_tags(self, language: LanguageEnum) -> list[Tag]:
        stmt = select(
            TagTranslateModel.tag_id,
            TagTranslateModel.name,
        ).where(TagTranslateModel.language_id == language)

        try:
            async with self.__session as session:
                tags = await session.execute(stmt)
            tags = tags.mappings().fetchall()
            if not tags:
                logger.warning(
                    "No tags found with language %s",
                    language,
                )
                return []
            return [Tag.model_validate(tag) for tag in tags]

        except DBAPIError as error:
            logger.error(
                "DB error when get tags with language %s",
                language,
                exc_info=error,
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


def article_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return ArticleRepository(session)
