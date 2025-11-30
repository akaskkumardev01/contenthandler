from pydantic import BaseModel
from fastapi_users import schemas
import uuid


class PostSchemaBody(BaseModel):
    title: str
    content: str


class PostSchemaResponse(BaseModel):
    title: str
    content: str

class UserCreate(schemas.BaseUserCreate):
    pass

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass