from pydantic import BaseModel
from datetime import datetime


class TaskCreate(BaseModel):
    name: str
    description: str


class TaskOut(BaseModel):
    id: int
    name: str
    description: str
    registry_date: datetime
    user_id: int

    model_config = {
        "from_attributes": True
    }