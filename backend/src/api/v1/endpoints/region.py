from fastapi import APIRouter, Depends, HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from api.v1.depends import language_dependency
from domain.entities.region import Region, RegionTranslateData
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryDoesNotExistsError,
    RegionAlreadyExistsError,
    RegionDatabaseError,
    RegionDoesNotExistsError,
    RegionIntegrityError,
)
from schemas.region_schema import RegionCreateSchema, RegionResponseSchema
from services.region_service import (
    RegionService,
    region_service_dependency,
)

router = APIRouter(prefix="/region", tags=["region"])


@router.post(
    "/",
    response_model=RegionResponseSchema,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_201_CREATED: {
            "detail": "Region create successfully.",
        },
        HTTP_404_NOT_FOUND: {
            "detail": "Country doesn't exists",
        },
        HTTP_409_CONFLICT: {
            "detail": "The region integrity error.",
        },
    },
)
async def create_region(
    region_schema: RegionCreateSchema,
    region_service: RegionService = Depends(region_service_dependency),
):
    # data preparation
    region = Region(
        region_id=region_schema.region_id,
        country_id=region_schema.country_id,
    )
    region_translate = RegionTranslateData(
        region_id=region_schema.region_id,
        name=region_schema.region_name,
        language_id=region_schema.language_id,
    )

    try:
        # === main logic ===
        await region_service.create_region(
            region=region,
            region_translate=region_translate,
        )

        return region_schema

    # === errors handling ===
    except RegionIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except RegionAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except CountryDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except RegionDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get("/{region_id}", response_model=RegionResponseSchema)
async def get_region(
    region_id: int,
    region_service: RegionService = Depends(region_service_dependency),
    language_id: LanguageEnum = Depends(language_dependency),
):
    try:
        region, region_translate = await region_service.get_region(
            region_id=region_id, language_id=language_id
        )

        return RegionResponseSchema(
            region_id=region.region_id,  # type: ignore
            region_name=region_translate.name,
            country_id=region.country_id,
            language_id=region_translate.language_id,
        )

    except RegionDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error

    except RegionIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error

    except RegionDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error
