from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, JSON, Enum as SqlAcademyEnum, Integer, Text
from typing import Optional, Union
from enum import Enum
from typing import Any

from object_types import RoleEnum


class BaseModel(DeclarativeBase):
    pass


class UserModel(BaseModel):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String())
    last_name: Mapped[Optional[str]]
    subscriber: Mapped["SubscriberModel"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    role: Mapped[RoleEnum] = mapped_column(
        SqlAcademyEnum(RoleEnum), default=RoleEnum.USER, nullable=True
    )

    def __repr__(self):
        return f"User: id={self.user_id}, first_name={self.first_name}, last_name={self.last_name}"


class SubscriberModel(BaseModel):
    __tablename__ = "subscriber"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey("user.user_id"), unique=True)
    chat_id: Mapped[int] = mapped_column(unique=True)
    signed: Mapped[bool] = mapped_column(default=False)
    user: Mapped["UserModel"] = relationship(
        back_populates="subscriber", passive_deletes=True
    )

    def __repr__(self):
        return f"Subscriber: user_id{self.user_id}, chat_id={self.chat_id}, signed={self.signed}"


class MailingContentModel(BaseModel):
    __tablename__ = "mailing_content"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(JSON, nullable=True)

    def __repr__(self):
        return f"MailingContentModel: id{self.id}, content={self.content}"


class LastMessage(BaseModel):
    __tablename__ = "last_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(Integer(), default=None, nullable=True)
    chat_id: Mapped[int] = mapped_column(Integer())
    text: Mapped[str] = mapped_column(Text())

    def __repr__(self):
        return f"LastMessage: id{self.id}, message_id={self.message_id}, chat_id={self.chat_id} text={self.text}"
