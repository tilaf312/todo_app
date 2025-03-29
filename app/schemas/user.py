from pydantic import BaseModel, constr
import re

PasswordStr = constr(min_length=1, pattern="^[A-Za-z0-9]+$")

class UserCreate(BaseModel):
    name: str
    password: PasswordStr


class UserOut(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }