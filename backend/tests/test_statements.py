"""
The file contains the test data for database.
This file has been created like the db/dependencies/base_statements.py file.
"""

from datetime import UTC, datetime

from sqlalchemy import insert
from tests.unit.constants import (
    BASE_ARTICLE_AUTHOR_ID,
    BASE_ARTICLE_CATEGORY_ID,
    BASE_ARTICLE_ID,
    BASE_ARTICLE_SLUG,
    BASE_ARTICLE_TITLE,
    BELARUS_ID,
    BELARUS_NAME,
    MOSCOW_REGION_ID,
    MOSCOW_REGION_NAME,
    NEW_GRAPE_ID,
    NEW_GRAPE_LANGUAGE,
    NEW_GRAPE_NAME,
    NEW_GRAPE_REGION_ID,
    PINOT_ARTICLE_ID,
    PINOT_ARTICLE_LANGUAGE,
    PINOT_ARTICLE_SLUG,
    PINOT_ARTICLE_TITLE,
    PINOT_GRAPE_ID,
    PINOT_GRAPE_LANGUAGE,
    PINOT_GRAPE_NAME,
    RUSSIA_ID,
    RUSSIA_NAME,
    SAMARA_REGION_ID,
    SAMARA_REGION_NAME,
)

from db.models import (
    Article,
    ArticleTranslate,
    Author,
    BlogCategory,
    BlogCategoryTranslate,
    Country,
    CountryTranslate,
    Grape,
    GrapeTranslate,
    Language,
    MdUser,
    Region,
    RegionTranslate,
    Role,
    Status,
    Tag,
    TagArticle,
    TagTranslate,
    User,
)
from db.statement import Statement
from domain.enums import ArticleStatus, LanguageEnum

# Tuple of insert statements for initial **test** data loading
TEST_STATEMENTS: tuple[Statement, ...] = (
    Statement(
        description="Insert language 'ru'",
        statement=insert(Language),
        data={"language_id": LanguageEnum.RUSSIAN, "name": "Russian"},
        check_query=lambda session: session.query(Language)
        .filter_by(language_id=LanguageEnum.RUSSIAN)
        .first(),
    ),
    Statement(
        description="Insert language 'en'",
        statement=insert(Language),
        data={"language_id": LanguageEnum.ENGLISH, "name": "English"},
        check_query=lambda session: session.query(Language)
        .filter_by(language_id=LanguageEnum.ENGLISH)
        .first(),
    ),
    Statement(
        description="Insert language 'ge'",
        statement=insert(Language),
        data={"language_id": "ge", "name": "German"},
        check_query=lambda session: session.query(Language)
        .filter_by(language_id="ge")
        .first(),
    ),
    Statement(
        description="Insert the test role",
        statement=insert(Role),
        data={"role_id": 1, "name": "Test Role"},
        check_query=lambda session: session.query(Role)
        .filter_by(role_id=1)
        .first(),
    ),
    Statement(
        description="Insert user 'Base User'",
        statement=insert(User),
        data={
            "user_id": BASE_ARTICLE_AUTHOR_ID,
            "login": "base_user",
            "email": "base_user@example.com",
            "password": "securepassword123",
            "role_id": 1,
            "is_registered": True,
        },
        check_query=lambda session: session.query(User)
        .filter_by(user_id=BASE_ARTICLE_AUTHOR_ID)
        .first(),
    ),
    Statement(
        description="Insert mduser",
        statement=insert(MdUser),
        data={
            "user_id": BASE_ARTICLE_AUTHOR_ID,
            "first_name": "John",
            "last_name": "Doe",
        },
        check_query=lambda session: session.query(MdUser)
        .filter_by(user_id=BASE_ARTICLE_AUTHOR_ID)
        .first(),
    ),
    Statement(
        description="Insert author 'Base Author'",
        statement=insert(Author),
        data={
            "user_id": BASE_ARTICLE_AUTHOR_ID,
            "work_place": "Test",
            "language_id": LanguageEnum.DEFAULT_LANGUAGE,
            "post": "CEO",
        },
        check_query=lambda session: session.query(Author)
        .filter_by(author_id=BASE_ARTICLE_AUTHOR_ID)
        .first(),
    ),
    Statement(
        description="Insert category 'Base Category'",
        statement=insert(BlogCategory),
        data={
            "blog_category_id": BASE_ARTICLE_CATEGORY_ID,
            "slug": "base-category",
        },
        check_query=lambda session: session.query(BlogCategory)
        .filter_by(category_id=BASE_ARTICLE_CATEGORY_ID)
        .first(),
    ),
    Statement(
        description="Insert category 'Base Category'",
        statement=insert(BlogCategoryTranslate),
        data={
            "blog_category_id": BASE_ARTICLE_CATEGORY_ID,
            "language_id": LanguageEnum.RUSSIAN,
            "name": "Base Category",
            "description": "Base Category Description",
        },
        check_query=lambda session: session.query(BlogCategoryTranslate)
        .filter_by(category_id=BASE_ARTICLE_CATEGORY_ID)
        .first(),
    ),
    Statement(
        description="Add status",
        statement=insert(Status),
        data={"status_id": 1},
        check_query=lambda session: session.query(Status)
        .filter_by(status_id=1)
        .first(),
    ),
    Statement(
        description="Add status",
        statement=insert(Status),
        data={"status_id": 2},
        check_query=lambda session: session.query(Status)
        .filter_by(status_id=2)
        .first(),
    ),
    Statement(
        description="Add status",
        statement=insert(Status),
        data={"status_id": 3},
        check_query=lambda session: session.query(Status)
        .filter_by(status_id=3)
        .first(),
    ),
    Statement(
        description="Insert article 'Pinot Article'",
        statement=insert(Article),
        data={
            "article_id": PINOT_ARTICLE_ID,
            "author_id": BASE_ARTICLE_AUTHOR_ID,
            "slug": PINOT_ARTICLE_SLUG,
            "blog_category_id": BASE_ARTICLE_CATEGORY_ID,
            "views_count": 50,
            "status_id": ArticleStatus.DRAFT,
            "published_at": datetime(year=2020, month=1, day=1, tzinfo=UTC),
        },
        check_query=lambda session: session.query(Article)
        .filter_by(article_id=PINOT_ARTICLE_ID)
        .first(),
    ),
    Statement(
        description="Insert article 'Base Article'",
        statement=insert(Article),
        data={
            "article_id": BASE_ARTICLE_ID,
            "author_id": BASE_ARTICLE_AUTHOR_ID,
            "slug": BASE_ARTICLE_SLUG,
            "blog_category_id": BASE_ARTICLE_CATEGORY_ID,
            "views_count": 100,
            "status_id": ArticleStatus.PUBLISHED,
        },
        check_query=lambda session: session.query(Article)
        .filter_by(article_id=BASE_ARTICLE_ID)
        .first(),
    ),
    Statement(
        description="Insert article translate data 'Pinot Article' ru",
        statement=insert(ArticleTranslate),
        data={
            "article_id": PINOT_ARTICLE_ID,
            "title": PINOT_ARTICLE_TITLE,
            "content": "# Pinot article content",
            "language_id": PINOT_ARTICLE_LANGUAGE,
            "image_src": "pinot_image.jpg",
        },
        check_query=lambda session: session.query(ArticleTranslate)
        .filter_by(article_id=PINOT_ARTICLE_ID)
        .first(),
    ),
    Statement(
        description="Insert article translate data 'Base Article' ru",
        statement=insert(ArticleTranslate),
        data={
            "article_id": BASE_ARTICLE_ID,
            "title": BASE_ARTICLE_TITLE,
            "content": "Base article content",
            "language_id": LanguageEnum.RUSSIAN,
            "image_src": "base_image.jpg",
        },
        check_query=lambda session: session.query(ArticleTranslate)
        .filter_by(article_id=BASE_ARTICLE_ID)
        .first(),
    ),
    Statement(
        description="Insert country 'Russia'",
        statement=insert(Country),
        data={"country_id": RUSSIA_ID},
        check_query=lambda session: session.query(Country)
        .filter_by(country_id=RUSSIA_ID)
        .first(),
    ),
    Statement(
        description="Insert country 'Belarus'",
        statement=insert(Country),
        data={"country_id": BELARUS_ID},
        check_query=lambda session: session.query(Country)
        .filter_by(country_id=BELARUS_ID)
        .first(),
    ),
    Statement(
        description="Insert translate country data 'Belarus'",
        statement=insert(CountryTranslate),
        data={
            "country_id": BELARUS_ID,
            "name": BELARUS_NAME,
            "language_id": LanguageEnum.RUSSIAN,
        },
        check_query=lambda session: session.query(CountryTranslate)
        .filter_by(country_id=BELARUS_ID)
        .first(),
    ),
    Statement(
        description="Insert translate country data 'Russia'",
        statement=insert(CountryTranslate),
        data={
            "country_id": RUSSIA_ID,
            "name": RUSSIA_NAME,
            "language_id": LanguageEnum.RUSSIAN,
        },
        check_query=lambda session: session.query(CountryTranslate)
        .filter_by(country_id=RUSSIA_ID)
        .first(),
    ),
    Statement(
        description="Insert region 'Samara'",
        statement=insert(Region),
        data={"country_id": RUSSIA_ID, "region_id": SAMARA_REGION_ID},
        check_query=lambda session: session.query(Region)
        .filter_by(region_id=SAMARA_REGION_ID)
        .first(),
    ),
    Statement(
        description="Insert region 'Moscow'",
        statement=insert(Region),
        data={"country_id": RUSSIA_ID, "region_id": MOSCOW_REGION_ID},
        check_query=lambda session: session.query(Region)
        .filter_by(region_id=MOSCOW_REGION_ID)
        .first(),
    ),
    Statement(
        description="Insert region translate data 'Samara' ru",
        statement=insert(RegionTranslate),
        data={
            "name": SAMARA_REGION_NAME,
            "region_id": SAMARA_REGION_ID,
            "language_id": LanguageEnum.RUSSIAN,
        },
        check_query=lambda session: session.query(RegionTranslate)
        .filter_by(region_id=SAMARA_REGION_ID)
        .first(),
    ),
    Statement(
        description="Insert region translate data 'Moscow' ru",
        statement=insert(RegionTranslate),
        data={
            "name": MOSCOW_REGION_NAME,
            "region_id": MOSCOW_REGION_ID,
            "language_id": LanguageEnum.RUSSIAN,
        },
        check_query=lambda session: session.query(RegionTranslate)
        .filter_by(region_id=MOSCOW_REGION_ID)
        .first(),
    ),
    Statement(
        description="Insert grape data 'Pinot noir'",
        statement=insert(Grape),
        data={
            "grape_id": PINOT_GRAPE_ID,
            "region_id": MOSCOW_REGION_ID,
        },
        check_query=lambda session: session.query(Grape)
        .filter_by(grape_id=PINOT_GRAPE_ID)
        .first(),
    ),
    Statement(
        description="Insert grape translate data 'Pinot noir' ru",
        statement=insert(GrapeTranslate),
        data={
            "grape_id": PINOT_GRAPE_ID,
            "name": PINOT_GRAPE_NAME,
            "language_id": PINOT_GRAPE_LANGUAGE,
        },
        check_query=lambda session: session.query(GrapeTranslate)
        .filter_by(grape_id=PINOT_GRAPE_ID)
        .first(),
    ),
    Statement(
        description="Insert grape data 'New Grape'",
        statement=insert(Grape),
        data={
            "grape_id": NEW_GRAPE_ID,
            "region_id": NEW_GRAPE_REGION_ID,
        },
        check_query=lambda session: session.query(Grape)
        .filter_by(grape_id=NEW_GRAPE_ID)
        .first(),
    ),
    Statement(
        description="Insert grape translate data 'New Grape' ru",
        statement=insert(GrapeTranslate),
        data={
            "grape_id": NEW_GRAPE_ID,
            "name": NEW_GRAPE_NAME,
            "language_id": NEW_GRAPE_LANGUAGE,
        },
        check_query=lambda session: session.query(GrapeTranslate)
        .filter_by(grape_id=NEW_GRAPE_ID)
        .first(),
    ),
    Statement(
        description="Insert tag",
        statement=insert(Tag),
        data={"tag_id": 101},
        check_query=lambda session: session.query(Tag)
        .filter_by(tag_id=101)
        .first(),
    ),
    Statement(
        description="Insert tag",
        statement=insert(Tag),
        data={"tag_id": 102},
        check_query=lambda session: session.query(Tag)
        .filter_by(tag_id=102)
        .first(),
    ),
    Statement(
        description="Insert tag",
        statement=insert(Tag),
        data={"tag_id": 103},
        check_query=lambda session: session.query(Tag)
        .filter_by(tag_id=103)
        .first(),
    ),
    Statement(
        description="Insert tag_translate",
        statement=insert(TagTranslate),
        data={
            "tag_id": 101,
            "language_id": LanguageEnum.RUSSIAN,
            "name": "new-tag",
        },
        check_query=lambda session: session.query(TagTranslate)
        .filter_by(tag_id=101)
        .first(),
    ),
    Statement(
        description="Insert tag_translate",
        statement=insert(TagTranslate),
        data={
            "tag_id": 102,
            "language_id": LanguageEnum.RUSSIAN,
            "name": "new-tag2",
        },
        check_query=lambda session: session.query(TagTranslate)
        .filter_by(tag_id=102)
        .first(),
    ),
    Statement(
        description="Insert tag_translate",
        statement=insert(TagTranslate),
        data={
            "tag_id": 103,
            "language_id": LanguageEnum.RUSSIAN,
            "name": "new-tag3",
        },
        check_query=lambda session: session.query(TagTranslate)
        .filter_by(tag_id=102)
        .first(),
    ),
    Statement(
        description="Insert tag_article",
        statement=insert(TagArticle),
        data={
            "tag_id": 101,
            "article_id": BASE_ARTICLE_ID,
        },
        check_query=lambda session: session.query(TagArticle)
        .filter_by(tag_id=101)
        .first(),
    ),
    Statement(
        description="Insert tag_article",
        statement=insert(TagArticle),
        data={
            "tag_id": 102,
            "article_id": PINOT_ARTICLE_ID,
        },
        check_query=lambda session: session.query(TagArticle)
        .filter_by(tag_id=102)
        .first(),
    ),
    Statement(
        description="Insert tag_article",
        statement=insert(TagArticle),
        data={
            "tag_id": 103,
            "article_id": PINOT_ARTICLE_ID,
        },
        check_query=lambda session: session.query(TagArticle)
        .filter_by(tag_id=103)
        .first(),
    ),
    Statement(
        description="Insert user 'Base User'",
        statement=insert(User),
        data={
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "login": "base_user2",
            "email": "base_user2@example.com",
            "password": "securepassword123",
            "role_id": 1,
            "is_registered": True,
        },
        check_query=lambda session: session.query(User)
        .filter_by(user_id="550e8400-e29b-41d4-a716-446655440000")
        .first(),
    ),
    Statement(
        description="Insert mduser",
        statement=insert(MdUser),
        data={
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "first_name": "John",
            "last_name": "Doe",
        },
        check_query=lambda session: session.query(MdUser)
        .filter_by(user_id="550e8400-e29b-41d4-a716-446655440000")
        .first(),
    ),
    Statement(
        description="Insert author 'Base Author'",
        statement=insert(Author),
        data={
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "work_place": "Test",
            "language_id": LanguageEnum.RUSSIAN,
            "post": "CEO",
        },
        check_query=lambda session: session.query(Author)
        .filter_by(author_id="550e8400-e29b-41d4-a716-446655440000")
        .first(),
    ),
    Statement(
        description="Insert article 'Merlot Article'",
        statement=insert(Article),
        data={
            "article_id": "223e4567-e89b-12d3-a456-426614174002",
            "author_id": "550e8400-e29b-41d4-a716-446655440000",
            "slug": "merlot-article",
            "blog_category_id": BASE_ARTICLE_CATEGORY_ID,
            "views_count": 75,
            "status_id": ArticleStatus.DRAFT,
            "published_at": datetime(year=2021, month=2, day=1, tzinfo=UTC),
        },
        check_query=lambda session: session.query(Article)
        .filter_by(article_id="223e4567-e89b-12d3-a456-426614174001")
        .first(),
    ),
    Statement(
        description="Insert article translate data 'Merlot Article' ru",
        statement=insert(ArticleTranslate),
        data={
            "article_id": "223e4567-e89b-12d3-a456-426614174002",
            "title": "Merlot Article",
            "content": "# Merlot article content",
            "language_id": LanguageEnum.RUSSIAN,
            "image_src": "merlot_image.jpg",
        },
        check_query=lambda session: session.query(ArticleTranslate)
        .filter_by(article_id="223e4567-e89b-12d3-a456-426614174002")
        .first(),
    ),
)


def get_test_statements() -> tuple[Statement, ...]:
    """
    Return the base statements for database configuration (for first startup)
    """
    return TEST_STATEMENTS
