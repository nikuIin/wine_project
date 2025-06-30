from fastapi import APIRouter, Depends, HTTPException, status

from domain.entities.region import Region
from domain.exceptions import (
    CountryDoesNotExistsError,
    RegionConflictError,
    RegionDatabaseError,
    RegionDoesNotExistsError,
)
from schemas.region_schema import RegionCreate, RegionUpdate
from use_cases.region_service import (
    RegionService,
    region_service_dependency,
)

e
router = APIRouter(prefix="/region", tags=["region"])


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
            region_id=region_id,
            new_region_data=updated_region,
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
