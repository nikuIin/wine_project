from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies.postgres_helper import postgres_helper
from domain.entities.user import UserBase, UserCreate, UserCreds
from repository.sql_queries.user_queries import CREATE_USER, GET_USER_CREDS


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_user_creds(self, login: str) -> UserCreds | None:
        async with self.__session as session:
            result = await session.execute(
                GET_USER_CREDS, params={"login": login}
            )
        result = result.mappings().fetchone()

        return UserCreds(**result) if result else None

    async def create_user(self, user: UserCreate) -> UserBase:
        async with self.__session as session:
            await session.execute(
                CREATE_USER,
                params={
                    "user_id": user.user_id,
                    "login": user.login,
                    "password": user.password,
                    "role_id": user.role_id,
                },
            )
            await session.commit()

        return UserBase(**user.model_dump())


def user_repository_dependency(
    session: AsyncSession = Depends(postgres_helper.session_dependency),
):
    return UserRepository(session=session)
