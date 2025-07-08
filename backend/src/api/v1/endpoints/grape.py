"""Grape API endpoints."""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.sql.expression import desc
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from api.v1.depends import language_dependency
from core.logger.logger import get_configure_logger
from domain.entities import grape
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


@router.post(
    "/",
    status_code=HTTP_201_CREATED,
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
        GrapeResponse: The created grape information.

    Raises:
        HTTPException:
            404 Not Found: If the specified region or language does not exist\n
            409 Conflict: If a grape with the same ID or name already exists\n
            500 Internal Server Error: For any other database-related errors\n
    """
    # === data preparation ===

    try:
        is_grape_created = await grape_service.create_grape(
            grape=grape_create,
        )

        if not is_grape_created:
            raise GrapeIntegrityError

        return {"detail": "Grape create succesfully."}

    # === errors handling ===
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


@router.get("/short_grapes", response_model=GrapeShortListSchema)
async def get_short_grapes(
    limit: LimitSchema = Depends(),
    offset: OffsetSchema = Depends(),
    language_id: LanguageEnum = Depends(language_dependency),
    grape_service: GrapeService = Depends(grape_service_dependency),
):
    try:
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
            language_model=language_id,
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


@router.get("/{grape_id}", response_model=GrapeResponseSchema)
async def get_grape(
    grape_id: UUID,
    grape_service: GrapeService = Depends(grape_service_dependency),
    language_id: LanguageEnum = Depends(language_dependency),
):
    """Get a specific grape variety by its ID."""
    try:
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
            language_model=language_id,
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


@router.put("/")
async def update_grape(
    # we dont use dependency of get_language becase the user should
    # be able to choose the language of the response
    grape_identify: GrapeIdentifySchema,
    grape_update: GrapeUpdateSchema = Body(),
    grape_service: GrapeService = Depends(grape_service_dependency),
):
    """Update a grape variety."""
    try:
        is_grape_updated = await grape_service.update_grape(
            grape_id=grape_identify.grape_id,
            language_id=grape_identify.language_model,
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


@router.delete("/{grape_id}")
async def delete_grape(
    grape_id: UUID,
    grape_service: GrapeService = Depends(grape_service_dependency),
):
    """Delete a grape variety by its ID."""
    try:
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
