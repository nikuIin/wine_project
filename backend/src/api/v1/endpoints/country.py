from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from api.v1.depends import language_dependency
from core.logger.logger import get_configure_logger
from domain.entities.country import Country, CountryTranslateData
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryDBError,
    CountryDoesNotExistsError,
    CountryIntegrityError,
)
from schemas.country_schema import (
    CountryCreateSchema,
    CountryCreateTranslateSchema,
    CountryListElement,
    CountryListResponseSchema,
    CountryResponseSchema,
    CountryResponseTranslateSchema,
)
from services.country_service import (
    CountryService,
    country_service_dependency,
)

router = APIRouter(prefix="/country", tags=["country"])

logger = get_configure_logger(Path(__file__).stem)


@router.post(
    "/",
    response_model=CountryResponseSchema,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_201_CREATED: {
            "detail": "Country create successfully.",
        },
        HTTP_409_CONFLICT: {
            "detail": "The country integrity error.",
        },
    },
)
async def create_country(
    country: CountryCreateSchema,
    country_service: CountryService = Depends(country_service_dependency),
):
    country_data = Country(
        country_id=country.country_id, flag_id=country.flag_id
    )
    country_translate_data = CountryTranslateData(
        country_id=country.country_id,
        name=country.country_name,
        language_id=country.data_language,
    )

    try:
        (
            country_data,
            country_translate_data,
        ) = await country_service.create_country(
            country=country_data,
            country_translate_data=country_translate_data,
        )

        return country
    # TODO: обработать ошибки FlagNotExistsError, LanguageNotExistsError
    except CountryIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except CountryDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.post(
    "/translate/{country_id}",
    response_model=CountryResponseTranslateSchema,
    responses={
        HTTP_201_CREATED: {
            "detail": "Country translate data create successfully.",
        },
        HTTP_404_NOT_FOUND: {
            "detail": (
                "The country which you need to create a translation"
                + " into another language does't exist."
            )
        },
        HTTP_409_CONFLICT: {
            "detail": "The country translate data integrity error.",
        },
    },
)
async def create_translate_country_data(
    country_translate_schema: CountryCreateTranslateSchema,
    country_id,
    country_service: CountryService = Depends(country_service_dependency),
):
    country_translate_data = CountryTranslateData(
        country_id=country_id,
        name=country_translate_schema.country_name,
        language_id=country_translate_schema.data_language,
    )

    try:
        country_translate_data = (
            await country_service.create_country_translate_data(
                country_translate_data=country_translate_data,
            )
        )

        return CountryResponseTranslateSchema(
            country_name=country_translate_data.name,
            data_language=country_translate_data.language_id,
        )

    # TODO: обработать ошибку LanguageNotExistsError
    except CountryDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except CountryIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except CountryDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.get("/all", response_model=CountryListResponseSchema)
async def gel_all_countries(
    country_service: CountryService = Depends(country_service_dependency),
    language_id: LanguageEnum = Depends(language_dependency),
):
    try:
        country_list = await country_service.get_all_countries(
            language_id=language_id
        )
        logger.info(country_list)
        country_list = [
            CountryListElement(
                country_id=country_data.country_id,
                country_name=country_translate.name,
                flag_url=country_data.flag_url,
            )
            for country_data, country_translate in country_list
        ]

        return CountryListResponseSchema(
            country_list=country_list,
            data_language=language_id,
        )
    except CountryIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except CountryDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get("/{country_id}", response_model=CountryResponseSchema)
async def get_country(
    country_id: int,
    country_service: CountryService = Depends(country_service_dependency),
    language_id: LanguageEnum = Depends(language_dependency),
):
    try:
        (
            country_data,
            country_translate_data,
        ) = await country_service.get_country_data(
            country_id=country_id, language_id=language_id
        )

        return CountryResponseSchema(
            country_id=country_data.country_id,
            country_name=country_translate_data.name,
            data_language=country_translate_data.language_id,
            flag_id=country_data.flag_id,
        )

    except CountryDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except CountryIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except CountryDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error
