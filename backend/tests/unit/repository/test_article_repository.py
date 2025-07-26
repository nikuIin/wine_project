from contextlib import nullcontext as dont_raise
from datetime import UTC, datetime, timezone
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
    PINOT_GRAPE_LANGUAGE,
    TAG_ID,
    TAG_NAME,
)

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
        "article_id, language, article_expectation, raise_excpecatation",
        [
            (
                PINOT_ARTICLE_ID,
                PINOT_ARTICLE_LANGUAGE,
                Article(
                    article_id=PINOT_ARTICLE_ID,
                    title=PINOT_ARTICLE_TITLE,
                    image_src="pinot_image.jpg",
                    content="# Pinot article content",
                    language=PINOT_ARTICLE_LANGUAGE,
                    author=Author(
                        author_id=BASE_ARTICLE_AUTHOR_ID,
                        first_name="John",
                        last_name="Doe",
                    ),
                    category=ArticleCategory(
                        category_id=BASE_ARTICLE_CATEGORY_ID,
                        name="Base Category",
                    ),
                    views_count=50,
                    status=ArticleStatus.DRAFT,
                    slug=PINOT_ARTICLE_SLUG,
                    published_at=datetime(
                        year=2020, month=1, day=1, tzinfo=UTC
                    ),
                    tags=[
                        Tag(tag_id=102, name="new-tag2"),
                        Tag(tag_id=103, name="new-tag3"),
                    ],
                ),
                dont_raise(),
            ),
            (
                "223e4567-e89b-12d3-a456-426614174002",  # New Merlot Article ID
                LanguageEnum.RUSSIAN,
                Article(
                    article_id=UUID("223e4567-e89b-12d3-a456-426614174002"),
                    title="Merlot Article",
                    image_src="merlot_image.jpg",
                    content="# Merlot article content",
                    language=LanguageEnum.RUSSIAN,
                    author=Author(
                        author_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
                        first_name="John",
                        last_name="Doe",
                    ),
                    category=ArticleCategory(
                        category_id=ArticleCategoriesID.RED_WINE,
                        name="Base Category",
                    ),
                    views_count=75,
                    status=ArticleStatus.DRAFT,
                    slug="merlot-article",
                    published_at=datetime(
                        year=2021, month=2, day=1, tzinfo=UTC
                    ),
                    tags=[],  # No tags
                ),
                dont_raise(),
            ),
            (
                "223e4567-e89b-12d3-a456-426614174006",
                LanguageEnum.RUSSIAN,
                None,
                dont_raise(),
            ),
            (
                "223e4567-e89b-12d3-a456-426614174002",
                LanguageEnum.KAZAKHSTAN,
                None,
                dont_raise(),
            ),
        ],
        ids=[
            "success_article_with_tags",
            "success_article_without_tags",
            "not_exists_article_with_definite_id",
            "not_exists_article_with_definite_language",
        ],
    )
    async def test_get_article(
        self,
        article_id: UUID,
        language: LanguageEnum,
        article_repository: ArticleRepository,
        article_expectation,
        raise_excpecatation,
    ):
        with raise_excpecatation:
            article = await article_repository.get_article(
                article_id=article_id, language=language
            )

            if article_expectation is None:
                assert article is article_expectation
            else:
                assert article is not None
                assert article.article_id == article_expectation.article_id
                assert article.title == article_expectation.title
                assert article.content == article_expectation.content
                assert article.slug == article_expectation.slug
                assert article.published_at == article_expectation.published_at
                assert article.category == article_expectation.category
                assert article.tags == article_expectation.tags
                assert article.author == article_expectation.author
                assert article.image_src == article_expectation.image_src
                assert article.views_count == article_expectation.views_count

    async def test_delete_article_success(
        self,
        article_repository: ArticleRepository,
        async_session: AsyncSession,
    ):
        rows = await article_repository.delete_article(
            article_id=PINOT_ARTICLE_ID,
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
            await article_repository.create_tag(tag)

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
            domain_tags = [
                Tag(tag_id=tag.tag_id, name=tag.name) for tag in tags
            ]
            await article_repository.set_tags_to_article(
                article_id, domain_tags
            )

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
