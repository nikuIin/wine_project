from contextlib import nullcontext as dont_raise
from uuid import UUID, uuid4

from pytest import fixture, mark, raises
from sqlalchemy import text
from sqlalchemy.ext.asyncio.session import AsyncSession
from tests.unit.constants import (
    BASE_ARTICLE_AUTHOR_ID,
    BASE_ARTICLE_CATEGORY_ID,
    BASE_ARTICLE_ID,
    BASE_ARTICLE_SLUG,
    BASE_ARTICLE_TITLE,
    NO_EXISTING_ARTICLE_ID,
    NO_EXISTING_AUTHOR_ID,
    NO_EXISTING_LANGUAGE_ID,
    PINOT_ARTICLE_ID,
    PINOT_ARTICLE_LANGUAGE,
    PINOT_ARTICLE_SLUG,
    PINOT_ARTICLE_TITLE,
    TAG_ID,
    TAG_NAME,
)

from domain.entities.tag import Tag
from domain.enums import ArticleStatus, LanguageEnum
from domain.exceptions import (
    ArticleAlreadyExistsError,
    ArticleDoesNotExistsError,
    ArticleIntegrityError,
    AuthorDoesNotExistsError,
    LanguageDoesNotExistsError,
    SlugAlreadyExistsError,
    TagAlreadyExistsError,
    TagDoesNotExistsError,
    TitleAlreadyExistsError,
)
from repository.article_repository import ArticleRepository
from schemas.article_schema import (
    ArticleCreateSchema,
    ArticleUpdateSchema,
    TagCreateSchema,
    TagGetSchema,
)


@fixture
def article_repository(async_session: AsyncSession):
    return ArticleRepository(session=async_session)


@mark.article
@mark.repository
@mark.asyncio
class TestArticleRepository:
    @mark.parametrize(
        "article, expectation",
        [
            (
                ArticleCreateSchema(
                    article_id=uuid4(),
                    author_id=BASE_ARTICLE_AUTHOR_ID,
                    slug="new-slug",
                    category_id=BASE_ARTICLE_CATEGORY_ID,
                    views_count=1,
                    status=ArticleStatus.DRAFT,
                    title="new-title",
                    content="New article content",
                    language=LanguageEnum.RUSSIAN,
                    image_src="new_image.jpg",
                ),
                dont_raise(),
            ),
            (
                ArticleCreateSchema(
                    article_id=uuid4(),
                    author_id=NO_EXISTING_AUTHOR_ID,
                    slug="new-slug",
                    category_id=BASE_ARTICLE_CATEGORY_ID,
                    views_count=1,
                    status=ArticleStatus.DRAFT,
                    title=BASE_ARTICLE_TITLE,
                    content="New article content",
                    language=LanguageEnum.RUSSIAN,
                    image_src="new_image.jpg",
                ),
                raises(AuthorDoesNotExistsError),
            ),
            (
                ArticleCreateSchema(
                    article_id=uuid4(),
                    author_id=BASE_ARTICLE_AUTHOR_ID,
                    slug="new-slug",
                    category_id=BASE_ARTICLE_CATEGORY_ID,
                    views_count=1,
                    status=ArticleStatus.DRAFT,
                    title=BASE_ARTICLE_TITLE,
                    content="New article content",
                    language=NO_EXISTING_LANGUAGE_ID,
                    image_src="new_image.jpg",
                ),
                raises(LanguageDoesNotExistsError),
            ),
            (
                ArticleCreateSchema(
                    article_id=uuid4(),
                    author_id=BASE_ARTICLE_AUTHOR_ID,
                    slug=PINOT_ARTICLE_SLUG,
                    category_id=BASE_ARTICLE_CATEGORY_ID,
                    views_count=1,
                    status=ArticleStatus.DRAFT,
                    title=BASE_ARTICLE_TITLE,
                    content="New article content",
                    language=LanguageEnum.RUSSIAN,
                    image_src="new_image.jpg",
                ),
                raises(SlugAlreadyExistsError),
            ),
            (
                ArticleCreateSchema(
                    article_id=BASE_ARTICLE_ID,
                    author_id=BASE_ARTICLE_AUTHOR_ID,
                    slug=BASE_ARTICLE_SLUG,
                    category_id=BASE_ARTICLE_CATEGORY_ID,
                    views_count=1,
                    status=ArticleStatus.DRAFT,
                    title=PINOT_ARTICLE_TITLE,
                    content="New article content",
                    language=LanguageEnum.RUSSIAN,
                    image_src="new_image.jpg",
                ),
                raises(ArticleAlreadyExistsError),
            ),
            (
                ArticleCreateSchema(
                    article_id=PINOT_ARTICLE_ID,
                    author_id=BASE_ARTICLE_AUTHOR_ID,
                    slug=BASE_ARTICLE_SLUG,
                    category_id=BASE_ARTICLE_CATEGORY_ID,
                    views_count=1,
                    status=ArticleStatus.DRAFT,
                    title=BASE_ARTICLE_TITLE,
                    content="New article content",
                    language=LanguageEnum.RUSSIAN,
                    image_src="new_image.jpg",
                ),
                raises(ArticleAlreadyExistsError),
            ),
        ],
        ids=(
            "success__create_article",
            "author_no_exists_error",
            "language_no_exists_error",
            "slug_unique_error",
            "title_unique_error",
            "article_already_exists_error",
        ),
    )
    async def test_article_insert(
        self,
        article: ArticleCreateSchema,
        article_repository: ArticleRepository,
        expectation,
        async_session: AsyncSession,
    ):
        with expectation:
            await article_repository.article_insert(article=article)

            # Verify insertion only for successful case
            if expectation is dont_raise():
                async with async_session:
                    result_article = await async_session.execute(
                        text(
                            """
                            select
                                article_id,
                                author_id,
                                slug,
                                category_id,
                                views_count,
                                status
                            from article
                            where article_id=:article_id
                            """
                        ),
                        params={"article_id": article.article_id},
                    )

                    result_article_translate = await async_session.execute(
                        text(
                            """
                            select
                                article_id,
                                title,
                                content,
                                image_src,
                                language_id
                            from article_translate
                            where article_id=:article_id and language_id=:language_id
                            """
                        ),
                        params={
                            "article_id": article.article_id,
                            "language_id": article.language,
                        },
                    )

                result_article = result_article.mappings().one_or_none()
                result_article_translate = (
                    result_article_translate.mappings().one_or_none()
                )

                assert result_article is not None
                assert result_article_translate is not None

                assert result_article.article_id == article.article_id
                assert result_article.author_id == article.author_id
                assert result_article.slug == article.slug
                assert result_article.category_id == article.category_id
                assert result_article.views_count == article.views_count
                assert result_article.status == article.status
                assert (
                    result_article_translate.article_id == article.article_id
                )
                assert result_article_translate.title == article.title
                assert result_article_translate.content == article.content
                assert result_article_translate.image_src == article.image_src
                assert result_article_translate.language_id == article.language

    @mark.parametrize(
        "article_id, language, update_article, expectation",
        [
            (
                PINOT_ARTICLE_ID,
                PINOT_ARTICLE_LANGUAGE,
                ArticleUpdateSchema(
                    author_id=BASE_ARTICLE_AUTHOR_ID,
                    slug=PINOT_ARTICLE_SLUG,
                    category_id=BASE_ARTICLE_CATEGORY_ID,
                    views_count=100,
                    status=ArticleStatus.PUBLISHED,
                    title=PINOT_ARTICLE_TITLE,
                    content="Updated content",
                    language=PINOT_ARTICLE_LANGUAGE,
                    image_src="updated_image.jpg",
                ),
                dont_raise(),
            ),
            (
                PINOT_ARTICLE_ID,
                PINOT_ARTICLE_LANGUAGE,
                ArticleUpdateSchema(
                    author_id=NO_EXISTING_AUTHOR_ID,
                    slug=PINOT_ARTICLE_SLUG,
                    category_id=BASE_ARTICLE_CATEGORY_ID,
                    views_count=100,
                    status=ArticleStatus.PUBLISHED,
                    title=BASE_ARTICLE_TITLE,
                    content="Updated content",
                    language=PINOT_ARTICLE_LANGUAGE,
                    image_src="updated_image.jpg",
                ),
                raises(AuthorDoesNotExistsError),
            ),
            (
                PINOT_ARTICLE_ID,
                LanguageEnum.KAZAKHSTAN,
                ArticleUpdateSchema(
                    author_id=BASE_ARTICLE_AUTHOR_ID,
                    slug=PINOT_ARTICLE_SLUG,
                    category_id=BASE_ARTICLE_CATEGORY_ID,
                    views_count=100,
                    status=ArticleStatus.PUBLISHED,
                    title=BASE_ARTICLE_TITLE,
                    content="Updated content",
                    language=LanguageEnum.KAZAKHSTAN,
                    image_src="updated_image.jpg",
                ),
                dont_raise(),
            ),
            (
                PINOT_ARTICLE_ID,
                PINOT_ARTICLE_LANGUAGE,
                ArticleUpdateSchema(
                    author_id=BASE_ARTICLE_AUTHOR_ID,
                    slug=BASE_ARTICLE_SLUG,
                    category_id=BASE_ARTICLE_CATEGORY_ID,
                    views_count=100,
                    status=ArticleStatus.PUBLISHED,
                    title=BASE_ARTICLE_TITLE,
                    content="Updated content",
                    language=PINOT_ARTICLE_LANGUAGE,
                    image_src="updated_image.jpg",
                ),
                raises(SlugAlreadyExistsError),
            ),
            (
                PINOT_ARTICLE_ID,
                PINOT_ARTICLE_LANGUAGE,
                ArticleUpdateSchema(
                    author_id=BASE_ARTICLE_AUTHOR_ID,
                    slug=PINOT_ARTICLE_SLUG,
                    category_id=BASE_ARTICLE_CATEGORY_ID,
                    views_count=100,
                    status=ArticleStatus.PUBLISHED,
                    title=BASE_ARTICLE_TITLE,
                    content="Updated content",
                    language=PINOT_ARTICLE_LANGUAGE,
                    image_src="updated_image.jpg",
                ),
                raises(TitleAlreadyExistsError),
            ),
        ],
        ids=(
            "success__update_article",
            "author_no_exists_error",
            "language_no_exists_error",
            "slug_unique_error",
            "title_unique_error",
        ),
    )
    async def test_update_article(
        self,
        article_id: UUID,
        language: LanguageEnum,
        update_article: ArticleUpdateSchema,
        article_repository: ArticleRepository,
        expectation,
        async_session: AsyncSession,
    ):
        with expectation:
            await article_repository.update_article(
                article_id=article_id,
                language=language,
                update_article=update_article,
            )

            # Verify updates only for successful case
            if expectation is dont_raise():
                async with async_session:
                    result_article = await async_session.execute(
                        text(
                            """
                            select
                                article_id,
                                author_id,
                                slug,
                                category_id,
                                views_count,
                                status
                            from article
                            where article_id=:article_id
                            """
                        ),
                        params={"article_id": article_id},
                    )

                    result_article_translate = await async_session.execute(
                        text(
                            """
                            select
                                article_id,
                                title,
                                content,
                                image_src
                            from article_translate
                            where article_id=:article_id and language_id=:language_id
                            """
                        ),
                        params={
                            "article_id": article_id,
                            "language_id": language.value,
                        },
                    )

                result_article = result_article.mappings().one_or_none()
                result_article_translate = (
                    result_article_translate.mappings().one_or_none()
                )

                assert result_article is not None
                assert result_article_translate is not None

                assert result_article.article_id == article_id
                assert result_article.author_id == update_article.author_id
                assert result_article.slug == update_article.slug
                assert result_article.category_id == update_article.category_id
                assert result_article.views_count == update_article.views_count
                assert result_article.status == update_article.status
                assert result_article_translate.article_id == article_id
                assert result_article_translate.title == update_article.title
                assert (
                    result_article_translate.content == update_article.content
                )
                assert (
                    result_article_translate.image_src
                    == update_article.image_src
                )

    async def test_delete_article_success(
        self,
        article_repository: ArticleRepository,
        async_session: AsyncSession,
    ):
        rows = await article_repository.delete_article(
            article_id=PINOT_ARTICLE_ID
        )
        assert rows == 2

        async with async_session:
            result_deleted = await async_session.execute(
                text(
                    """
                    select article_id from article_deleted where article_id=:article_id
                    """
                ),
                params={"article_id": PINOT_ARTICLE_ID},
            )
            result = await async_session.execute(
                text(
                    """
                    select article_id from article where article_id=:article_id
                    """
                ),
                params={"article_id": PINOT_ARTICLE_ID},
            )
            result_translate_deleted = await async_session.execute(
                text(
                    """
                    select article_id from article_translate_deleted where article_id=:article_id
                    """
                ),
                params={"article_id": PINOT_ARTICLE_ID},
            )
            result_translate = await async_session.execute(
                text(
                    """
                    select article_id from article_translate where article_id=:article_id
                    """
                ),
                params={"article_id": PINOT_ARTICLE_ID},
            )

            assert result.mappings().one_or_none() is None
            assert result_translate.mappings().one_or_none() is None
            assert result_deleted.mappings().one_or_none() is not None
            assert (
                result_translate_deleted.mappings().one_or_none() is not None
            )

    async def test_delete_article_not_existing(
        self,
        article_repository: ArticleRepository,
    ):
        rows = await article_repository.delete_article(
            article_id=NO_EXISTING_ARTICLE_ID
        )
        assert rows == 0

    @mark.parametrize(
        "tag, expectation",
        [
            (
                TagCreateSchema(
                    tag_id=100,
                    name="new_tag",
                    language=LanguageEnum.ENGLISH,
                ),
                dont_raise(),
            ),
            (
                TagCreateSchema(
                    tag_id=101,
                    name=TAG_NAME,
                    language=LanguageEnum.ENGLISH,
                ),
                raises(TagAlreadyExistsError),
            ),
        ],
        ids=("success__add_tag", "tag_already_exists_error"),
    )
    async def test_add_tag(
        self,
        tag: TagCreateSchema,
        expectation,
        article_repository: ArticleRepository,
        async_session: AsyncSession,
    ):
        with expectation:
            await article_repository.add_tag(tag)

            if expectation is dont_raise():
                result = await async_session.execute(
                    text(
                        """
                        select tag_id, name, language_id from tag_translate
                        where tag_id=:tag_id and language_id=:language_id
                        """
                    ),
                    params={"tag_id": tag.tag_id, "language_id": tag.language},
                )
                result = result.mappings().one_or_none()
                assert result is not None
                assert result.tag_id == tag.tag_id
                assert result.name == tag.name
                assert result.language_id == tag.language

    async def test_delete_tag_success(
        self,
        article_repository: ArticleRepository,
        async_session: AsyncSession,
    ):
        await article_repository.delete_tag(tag_id=TAG_ID)

        async with async_session:
            result = await async_session.execute(
                text(
                    """
                    select tag_id from tag where tag_id=:tag_id
                    """
                ),
                params={"tag_id": TAG_ID},
            )
            assert result.mappings().one_or_none() is None

    @mark.parametrize(
        "article_id, tags, expectation",
        [
            (
                PINOT_ARTICLE_ID,
                [
                    TagGetSchema(
                        tag_id=101,
                        name="new_tag_1",
                        language=LanguageEnum.ENGLISH,
                    ),
                ],
                dont_raise(),
            ),
            (
                PINOT_ARTICLE_ID,
                [
                    TagGetSchema(
                        tag_id=100,
                        name="new_tag_1",
                        language=LanguageEnum.ENGLISH,
                    ),
                ],
                raises(ArticleDoesNotExistsError),
            ),
            (
                NO_EXISTING_ARTICLE_ID,
                [
                    TagGetSchema(
                        tag_id=100,
                        name="new_tag_1",
                        language=LanguageEnum.ENGLISH,
                    )
                ],
                raises(ArticleDoesNotExistsError),
            ),
            (
                BASE_ARTICLE_ID,
                [
                    TagGetSchema(
                        tag_id=101,
                        name="new-tag",
                        language=LanguageEnum.ENGLISH,
                    )
                ],
                raises(TagAlreadyExistsError),
            ),
        ],
        ids=(
            "success__set_tags",
            "article_does_not_exists_error",
            "tag_does_not_exists",
            "tag_already_exists_error",
        ),
    )
    async def test_set_tags_to_article(
        self,
        article_id: UUID,
        tags: list[TagGetSchema],
        expectation,
        article_repository: ArticleRepository,
        async_session: AsyncSession,
    ):
        with expectation:
            await article_repository.set_tags_to_article(article_id, tags)

            if expectation is dont_raise():
                for tag in tags:
                    result = await async_session.execute(
                        text(
                            """
                            select tag_id from tag_article
                            where article_id=:article_id and tag_id=:tag_id
                            """
                        ),
                        params={
                            "article_id": article_id,
                            "tag_id": tag.tag_id,
                        },
                    )
                    assert result.mappings().one_or_none() is not None
