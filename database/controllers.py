from .models import User, Subscriber
from .core import engine
from sqlalchemy.orm import Session, relationship
from sqlalchemy import select
from typing import Optional, Callable, Any, Union


def create_user(
    user_id: int, first_name: str, chat_id: int, last_name: Optional[str] = None
):
    with Session(engine) as session:
        user = get_user(user_id=user_id)

        if user is None:
            try:
                user = User(user_id=user_id, first_name=first_name, last_name=last_name)
                session.add(user)
                session.commit()

                subscriber = Subscriber(chat_id=chat_id, signed=True, user=user)
                session.add(subscriber)
                session.commit()

                print("user", user, user.subscriber)

            except Exception as error:
                print("ошибка при создании пользователя: ", error)
                session.rollback()


def get_user(user_id: int) -> Union[User, None]:
    with Session(engine) as session:
        try:
            response = select(User).where(User.user_id == user_id)
            user = session.scalar(response)

            return user
        except Exception as error:
            return None


def subscribe(user_id: int) -> Union[Subscriber, None]:
    with Session(engine) as session:
        try:
            response = select(User).where(User.user_id == user_id)
            user = session.scalar(response)
            if user is not None:
                user.subscriber.signed = True
                session.commit()

                return user.subscriber
            else:
                return None
        except Exception as error:
            print("ошибка при подписке пользователя: ", error)
            return None


def unsubscribe(user_id: int) -> Union[Subscriber, None]:
    with Session(engine) as session:
        try:
            response = select(User).where(User.user_id == user_id)
            user = session.scalar(response)
            if user is not None:
                user.subscriber.signed = False
                session.commit()

                return user.subscriber
            else:
                return None
        except Exception as error:
            print("ошибка при отдписке пользователя: ", error)
            return None
