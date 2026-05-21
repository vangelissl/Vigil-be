class WrongPasswordError(Exception):
    def __init__(self, message: str = "Wrong password. Try again."):
        super().__init__(message)


class UnauthorizedUserError(Exception):
    def __init__(self, message: str = "Current user is not authorized"):
        super().__init__(message)
