from fastapi import APIRouter, Depends, HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from api.v1.depends import language_dependency
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryDBError,
    CountryDoesNotExistsError,
    CountryIntegrityError,
    LanguageDoesNotExistsError,
    RegionAlreadyExistsError,
    RegionDatabaseError,
    RegionDoesNotExistsError,
    RegionIntegrityError,
)
from schemas.country_schema import CountrySchema
from schemas.region_schema import (
    RegionCountryIDQuery,
    RegionCreateSchema,
    RegionIDQuery,
    RegionListElement,
    RegionListResponse,
    RegionResponseSchema,
    RegionTranslateCreateSchema,
)
from services.region_service import (
    RegionService,
    region_service_dependency,
)

router = APIRouter(prefix="/region", tags=["region"])


@router.post(
    "/",
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
    region_create: RegionCreateSchema,
    region_service: RegionService = Depends(region_service_dependency),
):
    try:
        # === main logic ===
        is_region_created = await region_service.create_region(
            region=region_create,
        )

        if is_region_created:
            return {"detail": "Region create successfully."}
        else:
            # TODO: add warning log message
            raise HTTPException(
                status_code=HTTP_409_CONFLICT, detail="Region inegrity error."
            )

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
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except RegionDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.post("/region_translate", status_code=HTTP_201_CREATED)
async def create_region_translate(
    region_translate_schema: RegionTranslateCreateSchema,
    region_id: RegionIDQuery = Depends(),
    region_service: RegionService = Depends(region_service_dependency),
):
    region_translate = RegionTranslateCreateSchema(
        region_name=region_translate_schema.region_name,
        language_model=region_translate_schema.language_model,
    )

    try:
        is_region_translate_created = (
            await region_service.create_region_translate(
                region_translate=region_translate, region_id=int(region_id)
            )
        )

        if is_region_translate_created:
            return {"detail": "Region translate created successfully"}
        else:
            # TODO: add warning log (этот код недостижим)
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="Region translate integrity error",
            )

    # === errors handling ===
    except RegionIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except RegionAlreadyExistsError as error:
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
    except RegionDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get("/region_list")
async def get_region_list(
    region_request: RegionCountryIDQuery = Depends(),
    language_id: LanguageEnum = Depends(language_dependency),
    region_service: RegionService = Depends(region_service_dependency),
):
    try:
        country, region_list = await region_service.get_region_list(
            country_id=region_request.country_id,
            language_id=language_id,
        )

        region_list = [
            RegionListElement(
                region_id=region.region_id,  # type: ignore
                region_name=region.name,
            )
            for region in region_list
        ]

        return RegionListResponse(
            country=CountrySchema(
                country_id=country.country_id,
                country_name=country.name,
            ),
            language_model=language_id,
            region_list=region_list,
        )

    except RegionDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except CountryDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except CountryIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except CountryDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error
    except RegionDatabaseError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get("/{region_id}", response_model=RegionResponseSchema)
async def get_region(
    region_id: RegionIDQuery = Depends(),
    region_service: RegionService = Depends(region_service_dependency),
    language_id: LanguageEnum = Depends(language_dependency),
):
    try:
        region = await region_service.get_region(
            region_id=int(region_id), language_id=language_id
        )

        if not region.country:
            raise RegionIntegrityError(
                "Region is not associated with a country"
            )

        return RegionResponseSchema(
            region_id=region.region_id,
            region_name=region.name,
            country=CountrySchema(
                country_id=region.country.country_id,
                country_name=region.country.name,
            ),
            language_model=language_id,
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
