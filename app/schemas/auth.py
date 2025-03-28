from pydantic import BaseModel


class AuthRequest(BaseModel):
    name: str
    password: str


class AuthResponse(BaseModel):
    message: str
