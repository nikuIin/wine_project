from pathlib import Path

from fastapi import Depends

from core.general_constants import DEFAULT_LIMIT
from core.logger.logger import get_configure_logger
from domain.exceptions import PartnerDatabaseError
from dto.partner_dto import PartnerDTO
from repository.partner_repository import (
    PartnerRepository,
    partner_repository_dependency,
)
from services.abc.partner_service_abc import AbstractPartnerService

logger = get_configure_logger(Path(__file__).stem)


class PartnerService(AbstractPartnerService):
    def __init__(self, partner_repo: PartnerRepository):
        self._partner_repo = partner_repo

    @staticmethod
    def partner_error_wrapper(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except PartnerDatabaseError as error:
                # TODO: mby add request to the Sentry
                raise error

        return wrapper

    @partner_error_wrapper
    async def get_partners(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> list[PartnerDTO]:
        partners = await self._partner_repo.get_partners(limit, offset)
        logger.info(partners)
        return partners


def partner_service_dependency(
    partner_repository: PartnerRepository = Depends(
        partner_repository_dependency
    ),
):
    return PartnerService(partner_repo=partner_repository)
