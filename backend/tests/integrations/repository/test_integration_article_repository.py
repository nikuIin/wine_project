from datetime import UTC, datetime
from uuid import UUID

from pytest import fixture, mark
from sqlalchemy.ext.asyncio import AsyncSession
from tests.unit.constants import (
    BASE_ARTICLE_AUTHOR_ID,
)

from domain.entities.article import Article, Author
from domain.entities.tag import Tag
from domain.enums import ArticleStatus, LanguageEnum
from repository.article_repository import ArticleRepository
from schemas.article_schema import (
    ArticleTranslateCreateSchema,
    TagCreateSchema,
    TagTranslateCreateSchema,
    TagTranslateUpdateSchema,
)


@fixture
def article_repository(async_session: AsyncSession):
    return ArticleRepository(session=async_session)


@mark.article
@mark.repository
@mark.integration
@mark.asyncio
class TestArticleRepository:
    async def test_article_integration_test(
        self, article_repository: ArticleRepository
    ):
        # Initialize article
        article = Article(
            article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
            title="Тестовый заголовок",
            slug="test-cool-article",
            author=Author(
                author_id=BASE_ARTICLE_AUTHOR_ID,
                first_name="John",
                last_name="Doe",
            ),
            image_src="test_image_src.webp",
            content="# Тестовый контент",
            views_count=1400,
            status=ArticleStatus.PUBLISHED,
            language=LanguageEnum.RUSSIAN,
            published_at=datetime(
                year=2020, month=10, day=5, hour=12, tzinfo=UTC
            ),
        )

        # Tests:
        # ======================================
        # Create article in russian
        await article_repository.article_insert(
            article=Article(
                article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
                title="Тестовый заголовок",
                slug="test-cool-article",
                author=Author(
                    author_id=BASE_ARTICLE_AUTHOR_ID,
                ),
                image_src="test_image_src.webp",
                content="# Тестовый контент",
                views_count=1400,
                status=ArticleStatus.PUBLISHED,
                language=LanguageEnum.RUSSIAN,
                published_at=datetime(
                    year=2020, month=10, day=5, hour=12, tzinfo=UTC
                ),
            )
        )
        # ======================================
        # Create translate to article in english
        await article_repository.insert_article_translate(
            article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
            language=LanguageEnum.ENGLISH,
            article_translate=ArticleTranslateCreateSchema(
                title="Test title",
                content="# Test content",
                image_src="test_image_english.webp",
            ),
        )
        # ======================================
        # Get article in russian
        assert article == await article_repository.get_article(
            article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
            language=LanguageEnum.RUSSIAN,
        )
        # ======================================
        # Get article in english
        article.language = LanguageEnum.ENGLISH
        article.title = "Test title"
        article.content = "# Test content"
        article.image_src = "test_image_english.webp"
        assert article == await article_repository.get_article(
            article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
            language=LanguageEnum.ENGLISH,
        )
        # ======================================
        # Add tag (global, not to article) in russian
        # Initialize tag
        tag = Tag(tag_id=1, name="2023 год")

        await article_repository.create_tag(
            tag=TagCreateSchema(
                tag_id=1,
                name="2023 год",
                language=LanguageEnum.RUSSIAN,
            )
        )
        # ======================================
        # Add translate for tag in english
        await article_repository.create_translate_to_tag(
            tag_id=1,
            language=LanguageEnum.ENGLISH,
            tag_translate=TagTranslateCreateSchema(
                name="2023 year",
            ),
        )
        # ======================================
        # Check that tag in the tag list
        assert tag in await article_repository.get_tags(
            language=LanguageEnum.RUSSIAN
        )
        # ======================================
        # Check that tag in english in the tag list
        tag.name = "2023 year"
        assert tag in await article_repository.get_tags(
            language=LanguageEnum.ENGLISH
        )
        # ======================================
        # Add this tag to the article
        await article_repository.set_tags_to_article(
            article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
            tags=[tag],
        )
        # ======================================
        # Change the tag russian version
        await article_repository.update_tag_translate(
            tag_id=1,
            tag_translate=TagTranslateUpdateSchema(
                name="2025 год",
                language=LanguageEnum.RUSSIAN,
            ),
            language=LanguageEnum.RUSSIAN,
        )
        # ======================================
        # Check that tag in the article
        tag.name = "2025 год"
        article_with_tags = await article_repository.get_article(
            article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
            language=LanguageEnum.RUSSIAN,
        )
        assert article_with_tags is not None

        assert tag in article_with_tags.tags
        # ======================================
        # Delete the tag
        await article_repository.delete_tag(tag_id=1)
        article_with_tags = await article_repository.get_article(
            article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
            language=LanguageEnum.RUSSIAN,
        )
        assert article_with_tags is not None
        assert article_with_tags.tags == []

        # ======================================
        # Delete translate in english from article
        await article_repository.delete_translate_article(
            article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
            language=LanguageEnum.ENGLISH,
        )

        assert (
            await article_repository.get_article(
                article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
                language=LanguageEnum.ENGLISH,
            )
            is None
        )
        assert (
            await article_repository.get_article(
                article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
                language=LanguageEnum.RUSSIAN,
            )
            is not None
        )
        # ======================================
        # Delete article
        await article_repository.delete_article(
            article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63")
        )

        assert (
            await article_repository.get_article(
                article_id=UUID("f9f2d4bb-a9e8-4594-9ddd-fd029742bc63"),
                language=LanguageEnum.RUSSIAN,
            )
            is None
        )
        # ======================================


@fixture
def some(quantity: int):
    return {"quantity": quantity}
