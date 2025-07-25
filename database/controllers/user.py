from ..models import UserModel, SubscriberModel, RoleEnum
from ..core import engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, Union
from object_types import RoleEnum
from helpers import session_decorator
from error_handlers import CreateUserError, GetUserError, RemoveUserError, AddUserError


@session_decorator(CreateUserError, "Ошибка при создании юзера в БД: ")
def create_user(
    user_id: int,
    first_name: str,
    chat_id: int,
    role: RoleEnum,
    session: Session,
    last_name: Optional[str] = None,
) -> Union[UserModel, None]:
    user_subscriber = get_user(user_id=user_id)

    if user_subscriber is None:
        user = UserModel(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        session.add(user)
        session.commit()

        subscriber = SubscriberModel(chat_id=chat_id, signed=True, user=user)
        session.add(subscriber)
        session.commit()
        return user

    return user_subscriber


@session_decorator(GetUserError, "Ошибка при полчения пользователя из БД: ")
def get_user(
    user_id: int,
    session: Session,
) -> Union[UserModel, None]:
    response = select(UserModel).where(UserModel.user_id == user_id)
    user = session.scalar(response)
    return user


@session_decorator(RemoveUserError, "Ошибка при удалении пользователя из БД: ")
def unsubscribe_user(user_id: int, session: Session):
    response = select(UserModel).where(UserModel.user_id == user_id)
    user = session.scalar(response)
    if user is not None:
        session.delete(user)
        session.commit()


@session_decorator(GetUserError, "Ошибка при полчения пользователей из БД: ")
def get_users(session: Session) -> list[SubscriberModel]:
    response = select(SubscriberModel).where(SubscriberModel.signed == True)
    users = session.scalars(response).all()
    return list(users)
