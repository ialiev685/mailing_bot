from pydantic import BaseModel
from typing import Optional, Literal, Union, List


class PhotoTypeModel(BaseModel):
    file_id: str
    width: int
    height: int


class MailingContentTypeModel(BaseModel):
    content_type: Literal["photo", "text"]
    text: Optional[str] = None
    photo: Optional[PhotoTypeModel] = None
