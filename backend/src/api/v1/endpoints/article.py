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
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from api.v1.depends import language_dependency
from core.general_constants import BASE_MAX_STR_LENGTH, BASE_MIN_STR_LENGTH
from core.logger.logger import get_configure_logger
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
    ContentTitleValidationError,
    LanguageDoesNotExistsError,
    SlugAlreadyExistsError,
    SlugIsMissingError,
    TagAlreadyExistsError,
    TagDatabaseError,
    TagDoesNotExistsError,
    TagIntegrityError,
    TitleAlreadyExistsError,
)
from schemas.article_schema import (
    ArticleCreateSchema,
    ArticleListSchema,
    ArticleResponseSchema,
    ArticleTranslateCreateSchema,
    ArticleTranslateUpdateSchema,
    ArticleUpdateSchema,
    TagCreateSchema,
    TagIDListRequest,
    TagIDRequest,
    TagTranslateCreateSchema,
    TagTranslateUpdateSchema,
)
from schemas.support_schemas import LimitSchema, OffsetSchema
from services.article_service import ArticleService, article_service_dependency

logger = get_configure_logger(Path(__file__).stem)


# Initialize FastAPI router for article-related endpoints.
router = APIRouter(prefix="/article", tags=["Article"])


@router.post("/tag/", status_code=HTTP_201_CREATED)
async def create_tag(
    tag_create: TagCreateSchema = Body(),
    article_service: ArticleService = Depends(article_service_dependency),
):
    try:
        await article_service.create_tag(tag=tag_create)
    except TagAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except TagDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except SlugAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except TitleAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except TagIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except TagDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.post(
    "/tag/translate/{tag_id}/{language}", status_code=HTTP_201_CREATED
)
async def add_translate_to_tag(
    language: LanguageEnum,
    tag_translate: TagTranslateCreateSchema,
    tag_id: TagIDRequest = Depends(),
    article_service: ArticleService = Depends(article_service_dependency),
):
    try:
        await article_service.create_translate_to_tag(
            tag_id=int(tag_id), language=language, tag_translate=tag_translate
        )

        return {"status": "success"}
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except TagDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except TagAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except TagIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except TagDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.put("/tag/translate/{tag_id}/{language}", status_code=HTTP_200_OK)
async def update_translate_of_tag(
    language: LanguageEnum,
    tag_translate: TagTranslateUpdateSchema,
    tag_id: TagIDRequest = Depends(),
    article_service: ArticleService = Depends(article_service_dependency),
):
    try:
        await article_service.update_translate_of_tag(
            tag_id=int(tag_id), language=language, tag_translate=tag_translate
        )

        return {"status": "success"}
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except TagDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except TagAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except TagIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except TagDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.post("/{article_id}/tags", status_code=HTTP_201_CREATED)
async def set_tags_to_article(
    article_id: UUID,
    tags: TagIDListRequest,
    article_service: ArticleService = Depends(article_service_dependency),
):
    try:
        await article_service.set_tags_to_article(
            tags=tags.tags, article_id=article_id
        )
        return {"message": "Tags set to the article."}
    except ArticleDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except TagAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except ArticleIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except ArticleDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get(
    "/all",
    summary="Retrieve a list of all articles",
    response_model=ArticleListSchema,
    description="""
    This endpoint allows fetching a paginated and sortable list of articles,
    with options to filter by categories, statuses, and tags.
    """,
    responses={
        200: {
            "description": "Successfully retrieved list of articles.",
        },
        400: {
            "description": (
                "Bad Request - Invalid input parameters "
                "(e.g., integrity error)."
            )
        },
        500: {
            "description": (
                "Internal Server Error - Database or service-level error."
            )
        },
    },
)
async def get_all_articles(
    offsets: OffsetSchema = Depends(),
    limits: LimitSchema = Depends(),
    order_by: ArticleSortBy = Query(default=ArticleSortBy.PUBLISHED_AT),
    order_direction: SortOrder = Query(default=SortOrder.DESC),
    searched_text: str | None = Query(
        default=None,
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
    ),
    categories_list: list[ArticleCategoriesID] = Query(
        default=[], description="List of article categories to filter by."
    ),
    statuses: list[ArticleStatus] = Query(
        default=[], description="List of article statuses to filter by."
    ),
    tags: list[int] = Query(
        default=[], description="List of tag IDs to filter by."
    ),
    language: LanguageEnum = Depends(language_dependency),
    article_service: ArticleService = Depends(article_service_dependency),
):
    """
    Retrieve a paginated and filtered list of articles.

    Args:
        offsets (OffsetSchema): Paging offset.
        limits (LimitSchema): Paging limit.
        order_by (ArticleSortBy): Field to sort articles by.
        order_direction (SortOrder): Sort order (ascending or descending).
        categories_list (list[ArticleCategory]): List of categories to
            filter articles.
        statuses (list[ArticleStatus]): List of statuses to filter articles.
        tags (list[int]): List of tag IDs to filter articles.
        language (LanguageEnum): The language of the articles to retrieve.
        article_service (ArticleService): Dependency for article-related
            operations.

    Returns:
        list[ArticleResponseSchema]: A list of articles matching the
            criteria.

    Raises:
        HTTPException:
            - 400 Bad Request: If there's an ArticleIntegrityError due to
              invalid query parameters.
            - 500 Internal Server Error: If a database error occurs during
              article retrieval.
    """
    try:
        # Call the article service to retrieve articles based on provided
        # filters and pagination.
        return await article_service.get_articles(
            language=language,
            category_id=tuple(categories_list) if categories_list else None,
            statuses=tuple(statuses) if statuses else None,
            tags=tuple(tags) if tags else None,
            searched_text=str(searched_text) if searched_text else None,
            limit=limits.limit,
            offset=offsets.offset,
            order_by=order_by,
            order_direction=order_direction,
        )
    except ContentTitleValidationError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except ArticleIntegrityError as error:
        # Handle cases where input parameters lead to data integrity issues.
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except ArticleDatabaseError as error:
        # Handle general database errors during the operation.
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get(
    "/{article_id}",
    response_model=ArticleResponseSchema,
    summary="Retrieve a single article by its ID",
    description="""
    This endpoint retrieves detailed information for a specific article
    using its unique identifier (UUID).
    """,
    responses={
        400: {
            "description": (
                "Bad Request - Invalid input (e.g., missing slug or "
                "integrity issue)."
            )
        },
        404: {
            "description": "Not Found - Article or related author does not exist."
        },
        500: {
            "description": (
                "Internal Server Error - Database or service-level error."
            )
        },
    },
)
async def get_article(
    article_id: UUID,
    language: LanguageEnum = Depends(language_dependency),
    article_service: ArticleService = Depends(article_service_dependency),
):
    """
    Retrieve a single article by its unique identifier.

    Args:
        article_id (UUID): The UUID of the article to retrieve.
        language (LanguageEnum): The language version of the article to
            retrieve.
        article_service (ArticleService): Dependency for article-related
            operations.

    Returns:
        ArticleResponseSchema: The detailed information of the requested
            article.

    Raises:
        HTTPException:
            - 400 Bad Request: If `SlugIsMissingError` or
              `ArticleIntegrityError` occurs.
            - 404 Not Found: If `AuthorDoesNotExistsError` or
              `ArticleDoesNotExistsError` occurs.
            - 500 Internal Server Error: If a database error occurs during
              article retrieval.
    """
    try:
        # Call the article service to fetch a single article by its ID.
        return await article_service.get_article(article_id, language)
    except ContentTitleValidationError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except SlugIsMissingError as error:
        # Handle cases where the article's slug is unexpectedly missing.
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except ArticleIntegrityError as error:
        # Handle cases where article data integrity is violated.
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except AuthorDoesNotExistsError as error:
        # Handle cases where the associated author for the article does not
        # exist.
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except ArticleDoesNotExistsError as error:
        # Handle cases where the requested article does not exist.
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except ArticleDatabaseError as error:
        # Handle general database errors during the operation.
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.post("/")
async def add_article(
    article: ArticleCreateSchema,
    article_service: ArticleService = Depends(article_service_dependency),
):
    try:
        # Call the article service to create a new article.
        return await article_service.add_article(article)
    except ContentTitleValidationError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except ArticleIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except AuthorDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except SlugAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except TitleAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except ArticleAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except ArticleDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.post("/translate/{article_id}/{language}")
async def add_translate_to_article(
    article_id: UUID,
    language: LanguageEnum,
    article_translate_data: ArticleTranslateCreateSchema,
    article_service: ArticleService = Depends(article_service_dependency),
):
    try:
        await article_service.add_translate_to_article(
            article_id=article_id,
            language=language,
            article_translate=article_translate_data,
        )
    except ContentTitleValidationError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except AuthorDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except SlugAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except TitleAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except ArticleAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except ArticleDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.put("/translate/{article_id}/{language}")
async def update_translate_article(
    article_id: UUID,
    language: LanguageEnum,
    article_translate_data: ArticleTranslateUpdateSchema,
    article_service: ArticleService = Depends(article_service_dependency),
):
    try:
        await article_service.update_translate_article(
            article_id=article_id,
            language=language,
            article_translate=article_translate_data,
        )
    except ContentTitleValidationError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except AuthorDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except SlugAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except TitleAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except ArticleAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except ArticleDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.put("/{article_id}")
async def update_article(
    article_id: UUID,
    article_update: ArticleUpdateSchema,
    language: LanguageEnum = Depends(language_dependency),
    article_service: ArticleService = Depends(article_service_dependency),
):
    try:
        # Call the article service to update an existing article.
        await article_service.update_article(
            article_id=article_id,
            article_update=article_update,
            language=language,
        )

        return {"status": "Article updated."}

    except ContentTitleValidationError as error:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error
    except AuthorIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except AuthorDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except TitleAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except TagAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except SlugAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except ArticleIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except ArticleDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.delete("/{article_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: UUID,
    article_service: ArticleService = Depends(article_service_dependency),
):
    try:
        await article_service.delete_article(
            article_id=article_id,
        )
    except ArticleDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.delete(
    "/translate/{article_id}/{language}", status_code=HTTP_204_NO_CONTENT
)
async def delete_translate_from_article(
    article_id: UUID,
    language: LanguageEnum,
    article_service: ArticleService = Depends(article_service_dependency),
):
    try:
        await article_service.delete_translate_from_article(
            article_id=article_id, language=language
        )
    except ArticleDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error
