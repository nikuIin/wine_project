from uuid import UUID

from fastapi import Depends

from domain.entities.grape import Grape
from domain.enums import LanguageEnum
from domain.exceptions import (
    GrapeAlreadyExistsError,
    GrapeDatabaseError,
    GrapeDoesNotExistsError,
    GrapeIntegrityError,
    LanguageDoesNotExistsError,
    RegionDoesNotExistsError,
)
from repository.grape_repository import (
    GrapeRepository,
    grape_repository_dependency,
)
from schemas.grape_schema import GrapeCreateSchema


class GrapeService:
    def __init__(self, grape_repository: GrapeRepository):
        self.__grape_repository = grape_repository

    async def create_grape(
        self,
        grape: GrapeCreateSchema,
    ) -> bool:
        try:
            return await self.__grape_repository.create_grape(
                grape=grape,
            )

        except GrapeIntegrityError as error:
            raise error
        except GrapeAlreadyExistsError as error:
            raise error
        except RegionDoesNotExistsError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except GrapeDatabaseError as error:
            raise error

    async def get_grape(
        self,
        grape_id: UUID,
        language_id: LanguageEnum = LanguageEnum.DEFAULT_LANGUAGE,
    ) -> Grape:
        try:
            return await self.__grape_repository.get_grape_by_id(
                grape_id=grape_id, language_id=language_id
            )

        except GrapeDoesNotExistsError as error:
            raise error
        except LanguageDoesNotExistsError as error:
            raise error
        except GrapeIntegrityError as error:
            raise error
        except GrapeDatabaseError as error:
            raise error


def grape_service_dependency(
    grape_repository: GrapeRepository = Depends(grape_repository_dependency),
):
    return GrapeService(grape_repository=grape_repository)
