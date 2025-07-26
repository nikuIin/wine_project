"""Grape API endpoints."""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from api.v1.depends import language_dependency
from core.logger.logger import get_configure_logger
from domain.enums import LanguageEnum
from domain.exceptions import (
    GrapeAlreadyExistsError,
    GrapeDatabaseError,
    GrapeDoesNotExistsError,
    GrapeIntegrityError,
    LanguageDoesNotExistsError,
    RegionDoesNotExistsError,
)
from schemas.country_schema import CountrySchema
from schemas.grape_schema import (
    GrapeCreateSchema,
    GrapeIdentifySchema,
    GrapeResponseSchema,
    GrapeShortListSchema,
    GrapeShortSchema,
    GrapeUpdateSchema,
)
from schemas.region_schema import RegionSchema
from schemas.support_schemas import LimitSchema, OffsetSchema
from services.grape_service import GrapeService, grape_service_dependency

router = APIRouter(prefix="/grape", tags=["grape"])

logger = get_configure_logger(Path(__file__).stem)


# TODO: move grape_id to service layer
# (generate automicity on the service layer instead web)
@router.post(
    "/",
    status_code=HTTP_201_CREATED,
    summary="Create a new grape variety.",
    description="This endpoint allows for the creation of a new grape variety.",
    response_description="A message indicating the success of the operation.",
    responses={
        HTTP_201_CREATED: {
            "description": "Grape created successfully.",
        },
        HTTP_404_NOT_FOUND: {
            "description": "Region or language not found.",
        },
        HTTP_409_CONFLICT: {
            "description": "Grape already exists or integrity error.",
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error.",
        },
    },
)
async def create_grape(
    grape_create: GrapeCreateSchema,
    grape_service: GrapeService = Depends(grape_service_dependency),
):
    """Create a new grape variety.

    This endpoint allows for the creation of a new grape variety along with
    its translation.

    Args:
        grape_create (GrapeCreate): The grape creation schema containing
        grape_id, region_id, grape_name, and language_model.
        grape_service (GrapeService): The dependency-injected grape service.

    Returns:
        dict: A message indicating the success of the operation.

    Raises:
        HTTPException:
            404 Not Found: If the specified region or language does not exist\n
            409 Conflict: If a grape with the same ID or name already exists\n
            500 Internal Server Error: For any other database-related errors\n
    """
    # This block attempts to create a new grape variety using the provided
    # data. It calls the service layer to handle the business logic of
    # creating the grape.
    try:
        is_grape_created = await grape_service.create_grape(
            grape=grape_create,
        )

        if not is_grape_created:
            raise GrapeIntegrityError

        return {"detail": "Grape create successfully."}

    # This block handles potential errors that can occur during the grape
    # creation process. It catches specific exceptions and returns the
    # appropriate HTTP status code and error message.
    except GrapeIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except GrapeAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except RegionDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except GrapeDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get(
    "/short_grapes",
    response_model=GrapeShortListSchema,
    summary="Get a short list of grape varieties.",
    description="This endpoint returns a paginated list of grape varieties.",
    response_description="A list of grape varieties.",
    responses={
        HTTP_404_NOT_FOUND: {
            "description": "Language not found.",
        },
        HTTP_409_CONFLICT: {
            "description": "Integrity error.",
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error.",
        },
    },
)
async def get_short_grapes(
    limit: LimitSchema = Depends(),
    offset: OffsetSchema = Depends(),
    language_id: LanguageEnum = Depends(language_dependency),
    grape_service: GrapeService = Depends(grape_service_dependency),
):
    """Get a short list of grape varieties.

    This endpoint returns a paginated list of grape varieties.

    Args:
        limit (LimitSchema): The maximum number of grapes to return.
        offset (OffsetSchema): The starting offset for the grape list.
        language_id (LanguageEnum): The language for the grape names.
        grape_service (GrapeService): The dependency-injected grape service.

    Returns:
        GrapeShortListSchema: A list of grape varieties.

    Raises:
        HTTPException:
            404 Not Found: If the specified language does not exist.\n
            409 Conflict: If there is an integrity error.\n
            500 Internal Server Error: For any other database-related errors.\n
    """
    try:
        # This block retrieves a list of grape varieties with minimal
        # information, suitable for display in a list.
        short_grapes = await grape_service.get_short_grapes(
            limit=int(limit),
            offset=int(offset),
            language_id=language_id,
        )

        if not short_grapes:
            raise GrapeDoesNotExistsError("The list of grapes is empty.")

        return GrapeShortListSchema(
            grapes=[
                GrapeShortSchema(
                    grape_id=short_grape.grape_id,
                    grape_name=short_grape.name,
                )
                for short_grape in short_grapes
            ],
            language=language_id,
        )

    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except GrapeIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except GrapeDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get(
    "/{grape_id}",
    response_model=GrapeResponseSchema,
    summary="Get a specific grape variety by its ID.",
    description="This endpoint returns a specific grape variety by its ID.",
    response_description="The grape variety information.",
    responses={
        HTTP_404_NOT_FOUND: {
            "description": "Grape or language not found.",
        },
        HTTP_409_CONFLICT: {
            "description": "Integrity error.",
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error.",
        },
    },
)
async def get_grape(
    grape_id: UUID,
    grape_service: GrapeService = Depends(grape_service_dependency),
    language_id: LanguageEnum = Depends(language_dependency),
):
    """Get a specific grape variety by its ID.

    Args:
        grape_id (UUID): The ID of the grape to retrieve.
        grape_service (GrapeService): The dependency-injected grape service.
        language_id (LanguageEnum): The language for the grape name.

    Returns:
        GrapeResponseSchema: The grape variety information.

    Raises:
        HTTPException:
            404 Not Found: If the grape or language does not exist.\n
            409 Conflict: If there is an integrity error.\n
            500 Internal Server Error: For any other database-related errors.\n
    """
    try:
        # This block retrieves a single grape variety by its ID.
        grape = await grape_service.get_grape_by_id(
            grape_id=grape_id,
            language_id=language_id,
        )

        if not grape.region or not grape.region.country:
            raise GrapeDoesNotExistsError(
                f"Grape with ID {grape_id} does not exist."
            )

        return GrapeResponseSchema(
            grape_id=grape.grape_id,
            grape_name=grape.name,
            region=RegionSchema(
                region_id=grape.region.region_id,
                region_name=grape.region.name,
                country=CountrySchema(
                    country_id=grape.region.country.country_id,
                    country_name=grape.region.country.name,
                ),
            ),
            language=language_id,
        )

    except GrapeDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except GrapeIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except GrapeDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.put(
    "/",
    summary="Update a grape variety.",
    description="This endpoint allows for updating a grape variety.",
    response_description="A message indicating the success of the operation.",
    responses={
        HTTP_404_NOT_FOUND: {
            "description": "Language or region not found.",
        },
        HTTP_409_CONFLICT: {
            "description": "Grape already exists or integrity error.",
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error.",
        },
    },
)
async def update_grape(
    # we dont use dependency of get_language because the user should
    # be able to choose the language of the response
    grape_identify: GrapeIdentifySchema = Query(),
    grape_update: GrapeUpdateSchema = Body(),
    grape_service: GrapeService = Depends(grape_service_dependency),
):
    """Update a grape variety.

    Args:
        grape_identify (GrapeIdentifySchema): The grape identification schema.
        grape_update (GrapeUpdateSchema): The grape update schema.
        grape_service (GrapeService): The dependency-injected grape service.

    Returns:
        dict: A message indicating the success of the operation.

    Raises:
        HTTPException:
            404 Not Found: If the language or region does not exist.\n
            409 Conflict: If the grape already exists or for integrity errors.\n
            500 Internal Server Error: For any other database-related errors.\n
    """
    try:
        # This block updates an existing grape variety with the provided data.
        is_grape_updated = await grape_service.update_grape(
            grape_id=grape_identify.grape_id,
            language_id=grape_identify.language,
            grape_update=grape_update,
        )

        if not is_grape_updated:
            raise GrapeIntegrityError(
                "The integrity error of update the grape."
                + " Try to change update data."
            )

        return {"detail": "Grape updated successfully."}

    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except GrapeAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except RegionDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except GrapeIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except GrapeDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.delete(
    "/{grape_id}",
    summary="Delete a grape variety by its ID.",
    description="This endpoint allows for deleting a grape variety by its ID.",
    response_description="A message indicating the success of the operation.",
    responses={
        HTTP_409_CONFLICT: {
            "description": "Integrity error.",
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error.",
        },
    },
)
async def delete_grape(
    grape_id: UUID,
    grape_service: GrapeService = Depends(grape_service_dependency),
):
    """Delete a grape variety by its ID.

    Args:
        grape_id (UUID): The ID of the grape to delete.
        grape_service (GrapeService): The dependency-injected grape service.

    Returns:
        dict: A message indicating the success of the operation.

    Raises:
        HTTPException:
            409 Conflict: If there is an integrity error.\n
            500 Internal Server Error: For any other database-related errors.\n
    """
    try:
        # This block deletes a grape variety by its ID.
        is_grape_deleted = await grape_service.delete_grape(grape_id=grape_id)

        if not is_grape_deleted:
            raise GrapeIntegrityError(
                "The integrity error of delete the grape."
            )

        return {"detail": "Grape deleted successfully."}

    except GrapeIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except GrapeDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error
