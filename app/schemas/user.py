from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }