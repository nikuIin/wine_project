from pathlib import Path

from fastapi import Depends
from sqlalchemy import delete, insert, update
from sqlalchemy.dialects.postgresql.base import select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.general_constants import DEFAULT_LIMIT
from core.logger.logger import get_configure_logger
from db.dependencies.postgres_helper import postgres_helper
from db.models import Partner
from domain.exceptions import PartnerDatabaseError
from dto.partner_dto import PartnerCreateDTO, PartnerDTO, PartnerUpdateDTO
from repository.abc.partner_repository_abc import AbstractPartnerRepository

logger = get_configure_logger(Path(__file__).stem)


class PartnerRepository(AbstractPartnerRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session

    @staticmethod
    def partner_error_wrapper(func):
        """Wrap partner repository methods to handle common database errors.

        This decorator catches SQLAlchemy database exceptions
        (IntegrityError and DBAPIError) that may occur during database
        operations and provides a consistent error handling mechanism
        for partner-related operations.

        Args:
            func: The async function to be wrapped

        Returns:
            The wrapped function with error handling
        """

        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except IntegrityError as error:
                # The partner table don't have integrity-errors
                raise error
            except DBAPIError as error:
                logger.error("DBError with partner data: %s", error)
                raise PartnerDatabaseError from error

        return wrapper

    @partner_error_wrapper
    async def get_partner(self, partner_id: int) -> PartnerDTO | None:
        """Retrieve a partner by their ID from the database.

        This method queries the database for a partner with the specified ID.
        If found, it returns a PartnerDTO object containing the partner's data.
        If no partner is found with the given ID, it returns None.

        Args:
            partner_id: The unique identifier of the partner to retrieve

        Returns:
            PartnerDTO: A data transfer object containing the partner's
            information if found, otherwise None
        """

        stmt = select(Partner).where(Partner.partner_id == partner_id)

        # Execute the query within an async session context
        async with self.__session as session:
            result = await session.execute(stmt)

        # Fetch the first result (or None if no results)
        partner = result.mappings().fetchone()

        # Convert the result to a PartnerDTO if found, otherwise return None
        return PartnerDTO.model_validate(partner) if partner else None

    @partner_error_wrapper
    async def get_partners(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> list[PartnerDTO]:
        """Retrieve a paginated list of partners from the database.

        This method queries the database for partners with pagination support.
        It returns a list of PartnerDTO objects containing the partners' data,
        limited by the specified limit and offset parameters.

        Args:
            limit: Maximum number of partners to return
            offset: Number of partners to skip before starting
                to return results

        Returns:
            list[PartnerDTO]: A list of PartnerDTO objects containing the
        partners' information.
        """
        # Create a SQLAlchemy select statement with pagination parameters
        stmt = (
            select(
                Partner.partner_id,
                Partner.name,
                Partner.image_src,
            )
            .limit(limit)
            .offset(offset)
        )

        # Execute the query within an async session context
        async with self.__session as session:
            result = await session.execute(stmt)

        partner_rows = result.mappings().all()

        # Convert the result to a list of PartnerDTO objects
        # Extract the Partner dictionary from each row before validation
        return [PartnerDTO.model_validate(row) for row in partner_rows]

    @partner_error_wrapper
    async def create_partner(
        self, partner_data: PartnerCreateDTO
    ) -> PartnerDTO:
        """Create a new partner in the database.

        Args:
            partner_data: Dictionary containing partner data to create

        Returns:
            PartnerDTO: The created partner data
        """
        stmt = (
            insert(Partner)
            .values(**partner_data.model_dump())
            .returning(Partner.partner_id)
        )

        async with self.__session as session:
            result = await session.execute(stmt)
            await session.commit()

        partner_id = result.scalar_one()

        return PartnerDTO(
            partner_id=partner_id,
            **partner_data.model_dump(),
        )

    @partner_error_wrapper
    async def update_partner(
        self,
        partner_id: int,
        partner_data: PartnerUpdateDTO,
    ) -> PartnerDTO | None:
        """Update an existing partner in the database.

        Args:
            partner_id: ID of the partner to update
            partner_data: Dictionary containing partner data to update

        Returns:
            PartnerDTO: The updated partner data if found, otherwise None
        """
        stmt = (
            update(Partner)
            .where(Partner.partner_id == partner_id)
            .values(**partner_data.model_dump())
            .returning(Partner)
        )

        async with self.__session as session:
            result = await session.execute(stmt)
            await session.commit()

            partner = result.mappings().fetchone()

        return PartnerDTO.model_validate(partner) if partner else None

    @partner_error_wrapper
    async def delete_partner(self, partner_id: int) -> bool:
        """Delete a partner from the database.

        Args:
            partner_id: ID of the partner to delete

        Returns:
            bool: True if partner was deleted, False if not found
        """
        stmt = (
            delete(Partner)
            .where(Partner.partner_id == partner_id)
            .returning(Partner.partner_id)
        )
        async with self.__session as session:
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar() is not None


def partner_repository_dependency(
    async_session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return PartnerRepository(async_session)
