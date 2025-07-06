"""Grape API endpoints."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from core.logger.logger import get_configure_logger
from domain.exceptions import (
    GrapeAlreadyExistsError,
    GrapeDatabaseError,
    GrapeIntegrityError,
    LanguageDoesNotExistsError,
    RegionDoesNotExistsError,
)
from schemas.grape_schema import GrapeCreateSchema, GrapeResponse
from services.grape_service import GrapeService, grape_service_dependency

router = APIRouter(prefix="/grape", tags=["grape"])

logger = get_configure_logger(Path(__file__).stem)


@router.post(
    "/",
    response_model=GrapeResponse,
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
            404 Not Found: If the specified region or language does not exist
            409 Conflict: If a grape with the same ID or name already exists
            500 Internal Server Error: For any other database-related errors
    """
    # === data preparation ===

    try:
        ...

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


@router.get("/{grapes}")
async def get_grapes():
    """Get all grape varieties."""
    ...


@router.get("/{grape_id}")
async def get_grape():
    """Get a specific grape variety by its ID."""
    ...


@router.put("/")
async def update_grape():
    """Update a grape variety."""
    ...


@router.delete("/{grape_id}")
async def delete_grape():
    """Delete a grape variety by its ID."""
    ...
