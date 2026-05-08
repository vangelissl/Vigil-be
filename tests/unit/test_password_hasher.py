from vigil.security.hashing import PasswordHasher


hasher = PasswordHasher()
password = "dummypass"

def test_same_password_not_equal_hashes():
	hash1 = hasher.hash(password)
	hash2 = hasher.hash(password)

	assert hash1 != hash2


def test_different_password_not_equal_hashes():
	password1 = password + "_1"
	password2 = password + "_2"

	hash1 = hasher.hash(password1)
	hash2 = hasher.hash(password2)

	assert hash1 != hash2


def test_verify_password():
	hash = hasher.hash(password)

	assert hasher.verify(password, hash)
