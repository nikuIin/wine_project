from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from core.general_constants import (
    BASE_MAX_STR_LENGTH,
    BASE_MIN_STR_LENGTH,
    MAX_COUNTRY_ID,
    MAX_DB_INT,
)
from domain.entities.region import Region
from domain.exceptions import (
    CountryDoesNotExistsError,
    RegionConflictError,
    RegionDatabaseError,
    RegionDoesNotExistsError,
)
from use_cases.region_service import (
    RegionService,
    region_service_dependency,
)

router = APIRouter(prefix="/region", tags=["region"])


class RegionCreate(BaseModel):
    region_id: int = Field(gt=0, lt=MAX_DB_INT)
    country_id: int = Field(gt=0, le=MAX_COUNTRY_ID)
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH,
        max_length=BASE_MAX_STR_LENGTH,
        examples=["Moscow area", "Москвоская область"],
    )


class RegionUpdate(BaseModel):
    region_id: int = Field(gt=0, lt=MAX_DB_INT)
    country_id: int = Field(gt=0, le=MAX_COUNTRY_ID)
    name: str = Field(
        min_length=BASE_MIN_STR_LENGTH, max_length=BASE_MAX_STR_LENGTH
    )


@router.post("/", response_model=Region, status_code=status.HTTP_201_CREATED)
async def create_region(
    region_create: RegionCreate,
    region_service: RegionService = Depends(region_service_dependency),
):
    region = Region(
        region_id=None,
        country_id=region_create.country_id,
        name=region_create.name,
    )
    try:
        created_region = await region_service.create_region(region)
        return created_region
    except CountryDoesNotExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except RegionConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Region already exists: {error}",
        ) from error
    except RegionDatabaseError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create region: {error}",
        ) from error


@router.get("/{region_id}", response_model=Region)
async def get_region(
    region_id: int,
    region_service: RegionService = Depends(region_service_dependency),
):
    try:
        region = await region_service.get_region_by_id(region_id)
        if region is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Region not found",
            )
        return region
    except RegionDatabaseError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.put("/{region_id}", response_model=Region)
async def update_region(
    region_id: int,
    region_update: RegionUpdate,
    region_service: RegionService = Depends(region_service_dependency),
):
    try:
        region = await region_service.get_region_by_id(region_id)
        if region is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Region not found",
            )

        updated_region = Region(
            region_id=region_update.region_id,
            country_id=region_update.country_id,
            name=region_update.name,
        )

        updated_region_result = await region_service.update_region(
            region_id=region_id, new_region_data=updated_region
        )

        if updated_region_result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Region not found",
            )
        return updated_region_result
    except CountryDoesNotExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except RegionDoesNotExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except RegionDatabaseError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_region(
    region_id: int,
    region_service: RegionService = Depends(region_service_dependency),
):
    try:
        await region_service.delete_region(region_id)

    except RegionDatabaseError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error
