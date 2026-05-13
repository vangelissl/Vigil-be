from dataclasses import dataclass


@dataclass
class RegisterDTO:
    email: str
    username: str
    password: str
    confirm_password: str


@dataclass
class LoginDTO:
    email: str
    password: str


@dataclass
class TokenPairDTO:
    access_token: str
    refresh_token: str