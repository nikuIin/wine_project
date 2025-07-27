from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from api.v1.depends import language_dependency
from core.logger.logger import get_configure_logger
from domain.enums import LanguageEnum
from domain.exceptions import (
    ContentAlreadyExistsError,
    ContentDBError,
    ContentDoesNotExistsError,
    ContentIntegrityError,
    ContentWithThisTitleAlreadyExistsError,
    LanguageDoesNotExistsError,
)
from schemas.content_schema import (
    ContentCreateSchema,
    ContentResponseSchema,
    ContentUpdateSchema,
)
from schemas.support_schemas import LimitSchema, OffsetSchema
from services.abc.content_service_abc import AbstractContentService
from services.content_service import (
    content_service_dependency,
)

logger = get_configure_logger(Path(__file__).stem)

router = APIRouter(prefix="/content", tags=["Content"])


@router.post(
    "/",
    status_code=HTTP_201_CREATED,
)
async def create_content(
    content_data: ContentCreateSchema = Body(),
    content_service: AbstractContentService = Depends(
        content_service_dependency
    ),
):
    try:
        content_id = await content_service.create(
            create_content_data=content_data
        )

        return {
            "content_id": content_id,
            "message": "Content created successfully.",
        }
    except (
        ContentAlreadyExistsError,
        ContentWithThisTitleAlreadyExistsError,
    ) as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except ContentIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except ContentDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.post(
    "/translate",
    status_code=HTTP_201_CREATED,
)
async def create_translate_to_content(
    content_id: UUID = Query(),
    content_data: ContentCreateSchema = Body(),
    content_service: AbstractContentService = Depends(
        content_service_dependency
    ),
):
    try:
        content_id = await content_service.create_translate(
            create_content_data=content_data,
            content_id=content_id,
        )

        return {
            "message": "Translate to content is created successfully.",
        }
    except (
        ContentAlreadyExistsError,
        ContentWithThisTitleAlreadyExistsError,
    ) as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except (LanguageDoesNotExistsError, ContentDoesNotExistsError) as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except ContentIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except ContentDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get("/name/{content_name}", response_model=ContentResponseSchema)
async def get_content_by_name(
    content_name: str,
    language: LanguageEnum = Depends(language_dependency),
    content_service: AbstractContentService = Depends(
        content_service_dependency
    ),
):
    try:
        content = await content_service.get_by_name(
            content_name=content_name, language=language
        )
        if content:
            return ContentResponseSchema(
                content_id=content.content_id,
                md_title=content.md_title,
                md_description=content.md_description,
                language=language,
                content=content.content,
            )
        else:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Content doesn't exists.",
            )
    except ContentDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except ContentDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get("/{content_id}", response_model=ContentResponseSchema)
async def get_content_by_id(
    content_id: UUID,
    language: LanguageEnum = Depends(language_dependency),
    content_service: AbstractContentService = Depends(
        content_service_dependency
    ),
):
    try:
        content = await content_service.get_by_id(
            content_id=content_id, language=language
        )

        if content:
            return ContentResponseSchema(
                content_id=content.content_id,
                md_title=content.md_title,
                md_description=content.md_description,
                language=language,
                content=content.content,
            )
        else:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Content doesn't exists.",
            )

    except ContentDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except ContentDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.put("/{content_id}", status_code=HTTP_200_OK)
async def update_content(
    content_id: UUID,
    content_data: ContentUpdateSchema,
    language: LanguageEnum = Depends(language_dependency),
    content_service: AbstractContentService = Depends(
        content_service_dependency
    ),
):
    try:
        rows_updated = await content_service.update(
            content_id=content_id, language=language, content_data=content_data
        )
        if not rows_updated:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Content not found"
            )
        return {"message": "Content updated successfully"}
    except (
        ContentAlreadyExistsError,
        ContentWithThisTitleAlreadyExistsError,
    ) as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except ContentIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except ContentDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.delete("/translation/{content_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_translation(
    content_id: UUID,
    language: LanguageEnum = Depends(language_dependency),
    content_service: AbstractContentService = Depends(
        content_service_dependency
    ),
):
    try:
        deleted_count = await content_service.delete_translation(
            content_id=content_id, language=language
        )
        if not deleted_count:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Translation not found"
            )
    except ContentDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.delete("/{content_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: UUID,
    content_service: AbstractContentService = Depends(
        content_service_dependency
    ),
):
    try:
        deleted_count = await content_service.delete(content_id=content_id)
        if not deleted_count:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Content not found"
            )
    except ContentDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get("/deleted/", response_model=list[ContentResponseSchema])
async def get_deleted_content(
    limit: LimitSchema = Depends(),
    offset: OffsetSchema = Depends(),
    content_service: AbstractContentService = Depends(
        content_service_dependency
    ),
):
    try:
        return await content_service.get_deleted(
            limit=limit.limit, offset=offset.offset
        )
    except ContentDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.post("/restore/{content_id}", status_code=HTTP_200_OK)
async def restore_content(
    content_id: UUID,
    language: LanguageEnum = Depends(language_dependency),
    content_service: AbstractContentService = Depends(
        content_service_dependency
    ),
):
    try:
        await content_service.restore(content_id=content_id, language=language)
        return {"message": "Content restored successfully"}
    except ContentAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except (ContentIntegrityError, ContentDBError) as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error
