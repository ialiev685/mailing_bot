from .models import UserModel, SubscriberModel, MailingContentModel

from .core import engine
from sqlalchemy.orm import Session, relationship
from sqlalchemy import select
from typing import Optional, Union
from object_types import MailingContentTypeModel


def create_user(
    user_id: int, first_name: str, chat_id: int, last_name: Optional[str] = None
) -> Union[UserModel, None]:
    with Session(engine) as session:
        user_subscriber = get_user(user_id=user_id)

        if user_subscriber is None:
            try:
                user = UserModel(
                    user_id=user_id, first_name=first_name, last_name=last_name
                )
                session.add(user)
                session.commit()

                subscriber = SubscriberModel(chat_id=chat_id, signed=True, user=user)
                session.add(subscriber)
                session.commit()

                print("user", user, user.subscriber)

            except Exception as error:
                print("Ошибка при создании пользователя: ", error)
                session.rollback()

                return None
        return user


def get_user(user_id: int) -> Union[UserModel, None]:
    with Session(engine) as session:
        try:
            response = select(UserModel).where(UserModel.user_id == user_id)
            user = session.scalar(response)

            return user
        except Exception as error:
            print("Ошибка при получении пользователя: ", error)
            return None


def subscribe_user(user_id: int) -> Union[SubscriberModel, None]:
    with Session(engine) as session:
        try:
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
    with Session(engine) as session:
        try:
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


def add_content(content_data: MailingContentTypeModel):

    try:
        with Session(engine) as session:
            mailing_content = MailingContentModel(
                content=content_data.model_dump_json()
            )
            session.add(mailing_content)
            session.commit()

            return mailing_content
            pass
    except Exception as error:
        print("Ошибка при добавлении контента в БД: ", error)
        raise


def get_content():
    pass


def remove_content():
    pass
