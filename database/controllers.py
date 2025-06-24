from .models import User, Subscriber
from .core import engine
from sqlalchemy.orm import Session
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

                subscriber = Subscriber(user_id=user.id, chat_id=chat_id, signed=True)
                session.add(subscriber)
                session.commit()

            except Exception as error:
                print("ошибка при создании пользователя: ", error)
                session.rollback()


def get_user(user_id: int) -> Union[User, None]:
    with Session(engine) as session:
        try:
            result = select(User).where(User.user_id == user_id)
            user = session.scalar(result)
        finally:
            session.close()
            return user


def subscribe():
    pass


def unsubscribe():
    pass
