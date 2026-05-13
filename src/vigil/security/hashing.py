from argon2.low_level import hash_secret, verify_secret, Type
from argon2.exceptions import VerifyMismatchError
import os

from typing import Final

TIME_COST_DEFAULT: Final = 3
MEMORY_COST_DEFAULT: Final = 64 * 1024
PARALLELISM_DEFAULT: Final = 4
HASH_LEN_DEFAULT: Final = 32
TYPE_DEFAULT: Final = Type.ID

class PasswordHasher:

	def hash(self, password: str) -> str:
		salt = os.urandom(16)

		hash = hash_secret(
			secret=password.encode("utf-8"), 
			salt=salt, 
			time_cost=TIME_COST_DEFAULT,
			memory_cost=MEMORY_COST_DEFAULT,
			parallelism=PARALLELISM_DEFAULT,
			hash_len=HASH_LEN_DEFAULT,
			type=TYPE_DEFAULT)
		
		return hash.decode("utf-8")
	
	def verify(self, password: str, hash: str) -> bool:
		try:
			return verify_secret(
				hash=hash.encode("utf-8"), 
				secret=password.encode("utf-8"), 
				type=TYPE_DEFAULT)
		
		except VerifyMismatchError:
			return False