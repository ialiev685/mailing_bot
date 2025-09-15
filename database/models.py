from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    ForeignKey,
    JSON,
    Enum as SqlAcademyEnum,
    BigInteger,
    Integer,
)
from typing import Optional
from object_types import RoleEnum


class BaseModel(DeclarativeBase):
    pass


class UserModel(BaseModel):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String)
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
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.user_id"), unique=True
    )
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True)
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


class StartMailingModel(BaseModel):
    __tablename__ = "start_mailing"
    name: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[bool] = mapped_column(default=False)


class OrderModel(BaseModel):
    __tablename__ = "create_order"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    current_step: Mapped[int] = mapped_column(Integer, default=1)
    to_country: Mapped[str] = mapped_column(String, nullable=True)
    count_people: Mapped[str] = mapped_column(String, nullable=True)
    count_days: Mapped[str] = mapped_column(String, nullable=True)
    month: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[str] = mapped_column(String, nullable=True)
    connection: Mapped[str] = mapped_column(String, nullable=True)
    is_created_order: Mapped[bool] = mapped_column(default=False)
    phone: Mapped[str] = mapped_column(nullable=True)
