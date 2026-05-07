from ....shared.base import Entity
from .value_objects import UserId, Email, Username


class User(Entity):

	def __init__(self, id: UserId, email: Email, username: Username, password_hash: str):
		self.id: UserId = id
		self.email: Email = email
		self.username: Username = username
		self.password_hash: str = password_hash