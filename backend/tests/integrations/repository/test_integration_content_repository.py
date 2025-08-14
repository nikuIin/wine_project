from uuid import uuid4

from pytest import fixture, mark
from sqlalchemy import text
from uuid_extensions import uuid7

from domain.entities.content import Content
from domain.enums import LanguageEnum
from dto.content_dto import ContentCreateDTO, ContentUpdateDTO
from repository.content_repository import (
    AbstractContentRepository,
    ContentRepository,
)
from schemas.content_schema import ContentCreateSchema, ContentUpdateSchema


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
        content_id = uuid7()
        content_create = ContentCreateDTO(
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
            language=LanguageEnum.ENGLISH,
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

        # 4. Update content
        update_content = ContentUpdateDTO(
            md_title="new_title",
            md_description="new_description",
            content={"b": 24, "c": 1234},
            language=LanguageEnum.ENGLISH,
        )

        rows_updated = await content_repository.update_content(
            content_id=content_id,
            language=LanguageEnum.RUSSIAN,
            content_data=update_content,
        )

        assert rows_updated == 1

        # 6. Get updated content

        content = await content_repository.get_content_by_id(
            content_id=content_id, language=LanguageEnum.ENGLISH
        )

        content_in.md_title = "new_title"
        content_in.md_description = "new_description"
        content_in.content = {"b": 24, "c": 1234}

        assert content == content_in

        # 7. Add content on Russian again
        await content_repository.create_content(
            create_content_data=content_create
        )

        # 8. Delete content on English

        rows_deleted = await content_repository.delete_translate_content(
            content_id=content_id,
            language=LanguageEnum.ENGLISH,
        )

        assert rows_deleted == 1

        content = await content_repository.get_content_by_id(
            content_id=content_id, language=LanguageEnum.ENGLISH
        )

        assert content is None

        # 9. Add content on English again
        content_create.md_title = "New english title"
        content_create.language = LanguageEnum.ENGLISH
        await content_repository.create_content(
            create_content_data=content_create
        )

        # 10. Delete content on all languages

        rows_deleted = await content_repository.delete_content(
            content_id=content_id,
        )

        assert rows_deleted == 2

        # 11. Get information of deleted content

        content_russian_in = Content(
            content_id=content_id,
            md_title="my_cute_title",
            md_description="my_cute_description",
            content={"a": 123},
            language=LanguageEnum.RUSSIAN,
        )

        content_english_in = Content(
            content_id=content_id,
            md_title="New english title",
            md_description="my_cute_description",
            content={"a": 123},
            language=LanguageEnum.ENGLISH,
        )

        deleted_content = await content_repository.get_deleted_content()
        assert len(deleted_content) == 2

        assert all(
            content in deleted_content
            for content in [content_russian_in, content_english_in]
        )

        # 12. Restore deleted content

        await content_repository.restore_content(
            content_id=content_id, language=LanguageEnum.RUSSIAN
        )

        restored_content = await content_repository.get_content_by_id(
            content_id=content_id, language=LanguageEnum.RUSSIAN
        )

        assert content_russian_in == restored_content
