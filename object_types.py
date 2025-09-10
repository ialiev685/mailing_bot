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

MailingContentGroupDict = dict[str, Union[MailingContentType, list[MailingContentType]]]


class RoleEnum(Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class OrderFieldsTypeModel(BaseModel):
    user_id: int
    current_step: int
    to_country: Optional[str] = None
    count_people: Optional[int] = None
    count_days: Optional[int] = None
    month: Optional[str] = None
    price: Optional[int] = None
    is_created_order: Optional[int] = None


FieldName = Literal[
    "user_id",
    "current_step",
    "to_country",
    "count_people",
    "count_days",
    "month",
    "price",
    "is_created_order",
]
