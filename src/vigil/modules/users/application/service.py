import uuid

from ....security.dependencies import PasswordHasher

from ..ports import UserRepositoryProtocol
from .dto import UserDTO, UpdateUserDTO
from .exceptions import WrongPasswordError

from ..domain.exceptions import UserNotFoundError, EmailAlreadyTakenError, UsernameAlreadyTakenError
from ..domain.value_objects import Username, Email


class UserService:
    def __init__(self, user_repo: UserRepositoryProtocol, hasher: PasswordHasher):
        self.user_repo = user_repo
        self.hasher = hasher

    async def get_current_user_profile(self, id: uuid.UUID) -> UserDTO:
        user = await self.user_repo.get(id)

        if not user:
            raise UserNotFoundError()

        return UserDTO(
            email=user.email.value,
            username=user.username.value
        )

    async def update_current_user_profile(self, id: uuid.UUID, update_user: UpdateUserDTO):
        user = await self.user_repo.get(id)

        if not user:
            raise UserNotFoundError()

        if not self.hasher.verify(update_user.password, user.password_hash):
            raise WrongPasswordError()

        if update_user.email and update_user.email != user.email.value and await self.user_repo.get_by_email(update_user.email):
            raise EmailAlreadyTakenError()

        if update_user.username and update_user.username != user.username.value and await self.user_repo.get_by_username(update_user.username):
            raise UsernameAlreadyTakenError()

        user.email = Email(
            update_user.email) if update_user.email and update_user.email != user.email.value else user.email
        user.username = Username(
            update_user.username) if update_user.username and update_user.username != user.username.value else user.username

        if update_user.new_password and update_user.new_password != update_user.password:
            user.password_hash = self.hasher.hash(update_user.new_password)

        await self.user_repo.update(id, user)
