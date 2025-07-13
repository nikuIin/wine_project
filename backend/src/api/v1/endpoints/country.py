from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from api.v1.depends import language_dependency
from core.logger.logger import get_configure_logger
from domain.entities.country import Country
from domain.enums import LanguageEnum
from domain.exceptions import (
    CountryAlreadyExistsError,
    CountryDBError,
    CountryDoesNotExistsError,
    CountryIntegrityError,
    LanguageDoesNotExistsError,
)
from schemas.country_schema import (
    CountryCreateSchema,
    CountryCreateTranslateSchema,
    CountryIDQuery,
    CountryListResponseSchema,
    CountryResponseSchema,
    CountrySchema,
)
from services.country_service import (
    CountryService,
    country_service_dependency,
)

router = APIRouter(prefix="/country", tags=["country"])

logger = get_configure_logger(Path(__file__).stem)


@router.post(
    "/",
    status_code=HTTP_201_CREATED,
    summary="Create a new country.",
    description="Create a new country with a name and a flag.",
    responses={
        HTTP_201_CREATED: {
            "description": "Country created successfully.",
        },
        HTTP_409_CONFLICT: {
            "description": "The country integrity error.",
        },
        HTTP_404_NOT_FOUND: {
            "description": "Language does not exist.",
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error.",
        },
    },
)
async def create_country(
    country: CountryCreateSchema,
    country_service: CountryService = Depends(country_service_dependency),
):
    """Create a new country with a name and a flag.

    Args:
        country (CountryCreateSchema): The country data to create.
        country_service (CountryService): The country service dependency.

    Returns:
        dict: A message indicating that the country was created successfully.

    Raises:
        HTTPException: If the country already exists, the language does not exist,
        or a database error occurs.
    """  # noqa: E501
    country_data = Country(
        country_id=country.country_id,
        name=country.country_name,
        flag_id=country.flag_id,
    )

    try:
        is_country_created = await country_service.create_country(
            country=country_data, language_id=country.language_model
        )

        if is_country_created:
            return {"detail": "Country create successfully."}
        else:
            # TODO: add warning log message
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="The country integrity error.",
            )

    except CountryIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except CountryAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except LanguageDoesNotExistsError as error:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except CountryDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from error


@router.post(
    "/translate/{country_id}",
    status_code=HTTP_201_CREATED,
    summary="Create a translation for a country.",
    description="Create a translation for a country in a specified language.",
    responses={
        HTTP_201_CREATED: {
            "description": "Country translate data create successfully.",
        },
        HTTP_404_NOT_FOUND: {
            "description": (
                "The country which you need to create a translation"
                + " into another language does't exist."
            )
        },
        HTTP_409_CONFLICT: {
            "description": "The country translate data integrity error.",
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error.",
        },
    },
)
async def create_translate_country_data(
    country_translate_schema: CountryCreateTranslateSchema,
    country_id: CountryIDQuery = Depends(),
    country_service: CountryService = Depends(country_service_dependency),
    language_id: LanguageEnum = Depends(language_dependency),
):
    """Create a translation for a country in a specified language.

    Args:
        country_translate_schema (CountryCreateTranslateSchema): The country translation data.
        country_id (CountryIDQuery): The ID of the country to translate.
        country_service (CountryService): The country service dependency.
        language_id (LanguageEnum): The language to translate the country to.

    Returns:
        dict: A message indicating that the country translation was created successfully.

    Raises:
        HTTPException: If the country does not exist, the language does not exist,
        or a database error occurs.
    """  # noqa: E501
    country = Country(
        country_id=int(country_id),
        name=country_translate_schema.country_name,
    )

    try:
        is_country_created = (
            await country_service.create_country_translate_data(
                country=country, language_id=language_id
            )
        )

        if is_country_created:
            return {"detail": "Country translate data created successfully."}
        else:
            # TODO: add warning log message
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="The country translate data integrity error.",
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


@router.get(
    "/all",
    response_model=CountryListResponseSchema,
    summary="Get all countries.",
    description="Return a list of all countries.",
    responses={
        HTTP_200_OK: {
            "description": "Successful Response",
        },
        HTTP_409_CONFLICT: {
            "description": "The country integrity error.",
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error.",
        },
    },
)
async def get_all_countries(
    country_service: CountryService = Depends(country_service_dependency),
    language_id: LanguageEnum = Depends(language_dependency),
):
    """Return a list of all countries.

    Args:
        country_service (CountryService): The country service dependency.
        language_id (LanguageEnum): The language to return the countries in.

    Returns:
        CountryListResponseSchema: A list of all countries.

    Raises:
        HTTPException: If a database error occurs.
    """
    try:
        country_list = await country_service.get_all_countries(
            language_id=language_id
        )
        logger.info(country_list)
        country_list = [
            CountrySchema(
                country_id=country_data.country_id,
                country_name=country_data.name,
                flag_url=country_data.flag_url,
            )
            for country_data in country_list
        ]

        return CountryListResponseSchema(
            countries=country_list,
            language_model=language_id,
        )
    except CountryIntegrityError as error:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except CountryDBError as error:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error


@router.get(
    "/{country_id}",
    response_model=CountryResponseSchema,
    summary="Get a country by ID.",
    description="Return a country by its ID.",
    responses={
        HTTP_200_OK: {
            "description": "Successful Response",
        },
        HTTP_404_NOT_FOUND: {
            "description": "Country does not exist.",
        },
        HTTP_409_CONFLICT: {
            "description": "The country integrity error.",
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error.",
        },
    },
)
async def get_country(
    country_id: CountryIDQuery = Depends(),
    country_service: CountryService = Depends(country_service_dependency),
    language_id: LanguageEnum = Depends(language_dependency),
):
    """Return a country by its ID.

    Args:
        country_id (int): The ID of the country to return.
        country_service (CountryService): The country service dependency.
        language_id (LanguageEnum): The language to return the country in.

    Returns:
        CountryResponseSchema: The country data.

    Raises:
        HTTPException: If the country does not exist or a database error occurs.
    """
    try:
        country_data = await country_service.get_country_data(
            country_id=int(country_id), language_id=language_id
        )

        return CountryResponseSchema(
            country_id=country_data.country_id,
            country_name=country_data.name,
            language_model=language_id,
            flag_url=country_data.flag_url,
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
