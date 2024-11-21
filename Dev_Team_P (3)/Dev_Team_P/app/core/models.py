from typing import Optional
import pydantic
import uuid


def generate_uuid() -> str:
    return str(uuid.uuid4())

class Document(pydantic.BaseModel):
    document_id: str = pydantic.Field(default_factory=generate_uuid)
    nombre: Optional[str] = None
    # user_id: str
    ruta: Optional[str] = None
    content: Optional[str] = None

class User(pydantic.BaseModel):
    id: Optional[str] = None
    username: str
    password: str