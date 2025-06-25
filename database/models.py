from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer, Engine
from typing import Optional


class BaseModel(DeclarativeBase):
    pass


class User(BaseModel):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String())
    last_name: Mapped[Optional[str]]
    subscriber: Mapped["Subscriber"] = relationship(
        back_populates="user", cascade="all, delete"
    )

    def __repr__(self):
        return f"User: id={self.user_id}, first_name={self.first_name}, last_name={self.last_name}"


class Subscriber(BaseModel):
    __tablename__ = "subscriber"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey("user.user_id"), unique=True)
    chat_id: Mapped[int] = mapped_column(unique=True)
    signed: Mapped[bool] = mapped_column(default=False)
    user: Mapped["User"] = relationship(
        back_populates="subscriber", cascade="save-update"
    )

    def __repr__(self):
        return f"Subscriber: user_id{self.user_id}, chat_id={self.chat_id}, signed={self.signed}"


def create_tables(engine: Engine):
    BaseModel.metadata.create_all(engine)
