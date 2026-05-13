import uuid

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..ports import UserRepositoryProtocol

from ..domain.exceptions import EmailAlreadyTakenError, UserAlreadyExistsError, UsernameAlreadyTakenError, UserNotFoundError
from ..domain.value_objects import UserId, Username, Email
from ..domain.entities import User

from vigil.core.database.models.user import UserModel


class UserRepository(UserRepositoryProtocol):

	def __init__(self, session: AsyncSession):
		self.session = session

	def _to_domain(self, user: UserModel) -> User:
		return User(
            id=UserId(user.id),
            email=Email(user.email),
            username=Username(user.username),
            password_hash=user.password_hash,
        )

	def _to_model(self, user: User) -> UserModel:
		return UserModel(
            id=user.id.value,
            email=user.email.value,
            username=user.username.value,
            password_hash=user.password_hash,
        )
	
	async def create(self, user:User) -> User:
		existing_user = (await self.session.execute(
			select(UserModel)
			.where(or_(
				UserModel.id == user.id.value,
				UserModel.email == user.email.value,
				UserModel.username == user.username.value
			))
		)).scalar()

		if not existing_user:
			model = self._to_model(user)
			self.session.add(model)
			await self.session.flush()
			return self._to_domain(model)
		else:
			if existing_user.email == user.email.value:
				raise EmailAlreadyTakenError()
			if existing_user.username == user.username.value:
				raise UsernameAlreadyTakenError()
			raise UserAlreadyExistsError()
	
	async def get(self, user_id: uuid.UUID) -> User:
		user = await self.session.get(UserModel, user_id)
		
		if not user:
			raise UserNotFoundError("user not found")
		return self._to_domain(user)
	
	async def get_by_email(self, email: str) -> User:
		user = (await self.session.execute(select(UserModel).where(UserModel.email == email))).scalar()
		if not user:
			raise UserNotFoundError("user not found")
		
		return self._to_domain(user)
	
	async def get_by_username(self, username: str) -> User:
		user = (await self.session.execute(select(UserModel).where(UserModel.username == username))).scalar()
		if not user:
			raise UserNotFoundError("user with this username not found")
		
		return self._to_domain(user)
	
	async def get_all(self, limit: int = 50, offset: int = 0) -> list[User]:
		models = (await self.session.scalars(
            select(UserModel).limit(limit).offset(offset)
        )).all()
		
		return [self._to_domain(m) for m in models]
	
	async def update(self, user_id: uuid.UUID, user: User):
		user_to_update = await self.session.get(UserModel, user_id)
		
		if not user_to_update:
			raise UserNotFoundError("user not found")
		user_to_update.email = user.email.value
		user_to_update.username = user.username.value
		user_to_update.password_hash = user.password_hash
		
		await self.session.flush()

	async def delete(self, user_id: uuid.UUID) -> bool:
		user_to_delete = await self.session.get(UserModel, user_id)
		
		if not user_to_delete:
			return False
		
		await self.session.delete(user_to_delete)
		await self.session.flush()
		
		return True