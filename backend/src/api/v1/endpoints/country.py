from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_409_CONFLICT

from domain.entities.country import Country
from domain.exceptions import (
    CountryAlreadyExistsError,
    CountryDBError,
    CountryDoesNotExistsError,
)
from schemas.country_schema import (
    CountryCreateSchema,
    CountrySchema,
    CountryUpdateSchema,
)
from services.country_service import (
    CountryService,
    country_service_dependency,
)

router = APIRouter(prefix="/country", tags=["country"])


@router.get("/{country_id}", response_model=CountrySchema)
async def get_country(
    country_id: int,
    country_service: CountryService = Depends(country_service_dependency),
):
    try:
        country = await country_service.get_country_by_id(country_id)
        if country is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found",
            )
        return country
    except CountryDBError as error:
        raise HTTPException(
            detail=str(error),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from error


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
    except CountryDBError as error:
        raise HTTPException(
            detail=str(error),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from error


@router.put("/{country_id}", response_model=Country)
async def update_country(
    country_id: int,
    country_data: CountryUpdateSchema,
    country_service: CountryService = Depends(country_service_dependency),
):
    try:
        updated_country_data = Country(
            country_id=country_data.country_id,
            name=country_data.name,
            flag_url=country_data.flag_url,
        )

        updated_country_result = await country_service.update_country(
            country_id=country_id,
            new_country_data=updated_country_data,
        )
        if updated_country_result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found",
            )
        return updated_country_result
    except CountryAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Country with id {country_data.country_id}"
                f" or name {country_data.name} already exists"
            ),
        ) from error
    except CountryDoesNotExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {country_id} doesn't exists.",
        ) from error

    except CountryDBError as error:
        raise HTTPException(
            detail=str(error),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from error


@router.delete("/{country_id}", status_code=status.HTTP_200_OK)
async def delete_country(
    country_id: int,
    country_service: CountryService = Depends(country_service_dependency),
):
    try:
        deleted_count = await country_service.delete_country(country_id)
        if not deleted_count:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found",
            )
        return {"rows_deleted": deleted_count}
    except CountryDBError as error:
        raise HTTPException(
            detail=str(error),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from error
