from domain.entities.user import UserBase, UserCreate, UserCreds
from repository.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.__user_repository = user_repository

    async def get_user_creds(self, login: str) -> UserCreds | None:
        return await self.__user_repository.get_user_creds(login=login)

    async def create_user(self, user: UserCreate) -> UserBase:
        return await self.__user_repository.create_user(user=user)
