from pydantic import BaseModel
from typing import Optional, Literal, Union, List


class Photo(BaseModel):
    file_id: str
    width: int
    height: int


class MailingContent(BaseModel):
    content_type: Literal["photo", "text"]
    text: Optional[str] = None
    photo: Optional[Union[Photo | List[Photo]]] = None
