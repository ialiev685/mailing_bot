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


class StatusABoutUsContent(Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"


class OrderFieldsTypeModel(BaseModel):
    user_id: int
    current_step: int
    to_country: Optional[str] = None
    count_people: Optional[str] = None
    count_days: Optional[str] = None
    month: Optional[str] = None
    price: Optional[str] = None
    is_created_order: bool
    connection: Optional[str] = None
    phone: Optional[str] = None


FieldName = Literal[
    "user_id",
    "current_step",
    "to_country",
    "count_people",
    "count_days",
    "month",
    "price",
    "is_created_order",
    "connection",
    "phone",
]
