from pydantic import BaseModel
from typing import Optional, Literal, Union
from typing import Optional
from enum import Enum


class MailingMediaContentTypeModel(BaseModel):
    file_id: str
    media_group_id: Optional[str] = None
    caption: Optional[str] = None


class MailingPhotoContentTypeModel(MailingMediaContentTypeModel):
    content_type: Literal["photo"]


class MailingVideoContentTypeModel(MailingMediaContentTypeModel):
    content_type: Literal["video"]


class MailingTextContentTypeModel(BaseModel):
    content_type: Literal["text"]
    text: Optional[str] = None
    media_group_id: None = None


MailingContentType = Union[
    MailingPhotoContentTypeModel,
    MailingVideoContentTypeModel,
    MailingTextContentTypeModel,
]


class RoleEnum(Enum):
    ADMIN = "ADMIN"
    USER = "ADMIN"
