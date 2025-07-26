from uuid import uuid4

from pytest import fixture, mark
from sqlalchemy import text

from domain.entities.content import Content
from domain.enums import LanguageEnum
from repository.content_repository import (
    AbstractContentRepository,
    ContentRepository,
)
from schemas.content_schema import ContentCreateSchema


@fixture
def content_repository(async_session):
    return ContentRepository(async_session=async_session)


@mark.content
@mark.repository
@mark.integration
class TestContentRepository:
    @mark.asyncio
    async def test_content_crud(
        self,
        content_repository: AbstractContentRepository,
        async_session,
    ):
        # 1. Create content
        content_id = uuid4()
        content_create = ContentCreateSchema(
            content_id=content_id,
            md_title="my_cute_title",
            md_description="my_cute_description",
            content={"a": 123},
            language=LanguageEnum.RUSSIAN,
        )

        await content_repository.create_content(
            create_content_data=content_create
        )

        # 2. Get content by id
        content = await content_repository.get_content_by_id(
            content_id=content_id, language=LanguageEnum.RUSSIAN
        )

        content_in = Content(
            content_id=content_id,
            md_title="my_cute_title",
            md_description="my_cute_description",
            content={"a": 123},
        )

        assert content is not None
        assert content.content_id == content_in.content_id
        assert content.content == content_in.content
        assert content.md_title == content_in.md_title
        assert content.md_description == content_in.md_description
        assert content.content == content_in.content

        # 3. Get content by name
        content = await content_repository.get_content_by_name(
            content_name="my_cute_title", language=LanguageEnum.RUSSIAN
        )

        assert content is not None
        assert content.content_id == content_in.content_id
        assert content.content == content_in.content
        assert content.md_title == content_in.md_title
        assert content.md_description == content_in.md_description
        assert content.content == content_in.content
