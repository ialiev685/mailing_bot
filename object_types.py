from pydantic import BaseModel
from typing import Optional, Literal
from typing import Optional
from enum import Enum


class PhotoTypeModel(BaseModel):
    file_id: str
    width: int
    height: int


class MailingContentTypeModel(BaseModel):
    content_type: Literal["photo", "text"]
    text: Optional[str] = None
    caption: Optional[str] = None
    photo: Optional[PhotoTypeModel] = None


class RoleEnum(Enum):
    ADMIN = "ADMIN"
    USER = "ADMIN"
