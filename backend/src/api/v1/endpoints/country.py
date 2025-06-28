from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_409_CONFLICT

from domain.entities.country import Country
from domain.exceptions import CountryAlreadyExistsError
from schemas.country_schema import (
    CountryCreateSchema,
    CountrySchema,
    CountryUpdateSchema,
)
from use_cases.country_service import (
    CountryService,
    country_service_dependency,
)

router = APIRouter(prefix="/country", tags=["country"])


@router.get("/{country_id}", response_model=CountrySchema)
async def get_country(
    country_id: int,
    country_service: CountryService = Depends(country_service_dependency),
):
    country = await country_service.get_country_by_id(country_id)
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found",
        )
    return country


@router.post(
    "/",
    response_model=Country,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Country created successfully"},
        409: {"description": "Country with this ID/Name already exists"},
    },
)
async def create_country(
    country_data: CountryCreateSchema,
    country_service: CountryService = Depends(country_service_dependency),
):
    try:
        country = Country(
            country_id=country_data.country_id,
            name=country_data.name,
            flag_url=country_data.flag_url,
        )
        created_country = await country_service.create_country(country)
        return created_country
    except CountryAlreadyExistsError as error:
        raise HTTPException(
            detail=str(error),
            status_code=HTTP_409_CONFLICT,
        ) from error


@router.put("/{country_id}", response_model=Country)
async def update_country(
    country_id: int,
    country_data: CountryUpdateSchema,
    country_service: CountryService = Depends(country_service_dependency),
):
    country = await country_service.get_country_by_id(country_id)
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
        )

    updated_country = Country(
        country_id=country_id,
        name=country_data.name,
        flag_url=country_data.flag_url,
    )

    updated_country_result = await country_service.update_country(
        updated_country
    )
    if updated_country_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
        )
    return updated_country_result


@router.delete("/{country_id}", status_code=status.HTTP_200_OK)
async def delete_country(
    country_id: int,
    country_service: CountryService = Depends(country_service_dependency),
):
    deleted_count = await country_service.delete_country(country_id)
    if not deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
        )
    return {"rows_deleted": deleted_count}
