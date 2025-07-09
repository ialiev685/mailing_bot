from .models import (
    UserModel,
    SubscriberModel,
    MailingContentModel,
    RoleEnum,
    LastMessage,
)
from helpers import parse_and_sort_content, session_decorator
from .core import engine
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, desc
from typing import Optional, Union
from object_types import RoleEnum, MailingContentType
from error_handlers import AddMailingContentError, AddLastMessageError
from telebot import TeleBot


def create_user(
    user_id: int,
    first_name: str,
    chat_id: int,
    role: RoleEnum,
    last_name: Optional[str] = None,
) -> Union[UserModel, None]:
    user_subscriber = get_user(user_id=user_id)

    if user_subscriber is None:
        with Session(engine) as session:

            try:
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
            except Exception as error:
                print("Ошибка при создании пользователя: ", error)
                session.rollback()

                return None
    return user_subscriber


def get_user(user_id: int) -> Union[UserModel, None]:
    try:
        with Session(engine) as session:
            response = select(UserModel).where(UserModel.user_id == user_id)
            user = session.scalar(response)

            return user
    except Exception as error:
        print("Ошибка при получении пользователя: ", error)
        return None


def subscribe_user(user_id: int) -> Union[SubscriberModel, None]:
    try:
        with Session(engine) as session:
            response = select(UserModel).where(UserModel.user_id == user_id)
            user = session.scalar(response)
            if user is not None:
                user.subscriber.signed = True
                session.commit()

                return user.subscriber
            else:
                return None
    except Exception as error:
        print("Ошибка при подписке пользователя: ", error)
        return None


def unsubscribe_user(user_id: int) -> Union[SubscriberModel, None]:
    try:
        with Session(engine) as session:
            response = select(UserModel).where(UserModel.user_id == user_id)
            user = session.scalar(response)
            if user is not None:
                user.subscriber.signed = False
                session.commit()

                return user.subscriber
            else:
                return None
    except Exception as error:
        print("Ошибка при отдписке пользователя: ", error)
        return None


def get_users() -> list[SubscriberModel]:
    try:
        with Session(engine) as session:
            response = select(SubscriberModel).where(SubscriberModel.signed == True)
            users = session.scalars(response).all()

            return list(users)
    except Exception as error:
        raise


def add_mailing_content(content_data: MailingContentType):

    try:
        with Session(engine) as session:
            mailing_content = MailingContentModel(
                content=content_data.model_dump_json()
            )

            session.add(mailing_content)
            session.commit()

            return mailing_content

    except Exception as error:
        raise AddMailingContentError("Ошибка при добавлении контента в БД", error)


def get_mailing_content():
    try:

        with Session(engine) as session:

            response = select(MailingContentModel)
            content = session.scalars(response).all()

            return parse_and_sort_content(list(content))

    except Exception as error:
        print("Ошибка при получении контента в БД: ", error)
        raise


def remove_content():
    try:
        with Session(engine) as session:
            response = delete(MailingContentModel)
            session.execute(response)
            session.commit()

    except Exception as error:
        raise


@session_decorator(
    AddLastMessageError, "Ошибка при добавлении последнего сообщения в БД"
)
def add_last_message(chat_id: int, text: str, session: Session):

    remove_last_message()

    last_message = LastMessage(chat_id=chat_id, text=text)
    session.add(last_message)
    session.commit()

    raise AddLastMessageError("Упс")


def get_last_message():
    try:
        with Session(engine) as session:
            response = select(LastMessage).order_by(desc(LastMessage.id))
            last_message = session.scalars(response).first()

            return last_message

    except Exception as error:
        raise


def remove_last_message():
    try:
        with Session(engine) as session:
            response = delete(LastMessage)
            session.execute(response)
            session.commit()

    except Exception as error:
        raise
