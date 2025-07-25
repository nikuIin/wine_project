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
from schemas.grape_schema import GrapeCreateSchema, GrapeUpdateSchema


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

    async def get_grape_by_id(
        self, grape_id: UUID, language_id: LanguageEnum
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

    async def get_short_grapes(
        self,
        offset: int,
        limit: int,
        language_id: LanguageEnum,
    ) -> list[Grape]:
        try:
            return await self.__grape_repository.get_short_grapes(
                language_id=language_id,
                limit=limit,
                offset=offset,
            )

        except LanguageDoesNotExistsError as error:
            raise error
        except GrapeIntegrityError as error:
            raise error
        except GrapeDatabaseError as error:
            raise error

    async def update_grape(
        self,
        grape_id: UUID,
        grape_update: GrapeUpdateSchema,
        language_id: LanguageEnum,
    ) -> bool:
        try:
            return bool(
                await self.__grape_repository.update_grape(
                    grape_id=grape_id,
                    language_id=language_id,
                    grape_update=grape_update,
                )
            )

        except LanguageDoesNotExistsError as error:
            raise error
        except GrapeAlreadyExistsError as error:
            raise error
        except RegionDoesNotExistsError as error:
            raise error
        except GrapeIntegrityError as error:
            raise error
        except GrapeDatabaseError as error:
            raise error

    async def delete_grape(
        self,
        grape_id: UUID,
    ) -> bool:
        try:
            return bool(
                await self.__grape_repository.delete_grape(
                    grape_id=grape_id,
                )
            )

        except GrapeIntegrityError as error:
            raise error
        except GrapeDatabaseError as error:
            raise error


def grape_service_dependency(
    grape_repository: GrapeRepository = Depends(grape_repository_dependency),
):
    return GrapeService(grape_repository=grape_repository)
