from vigil.shared.base import Entity
from .value_objects import UserId, Email


class User(Entity):

	def __init__(self, id: UserId, email: Email, password_hash: str):
		self.id: UserId = id
		self.email: Email = email
		self.password_hash: str = password_hash