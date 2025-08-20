from ..models import LastMessage
from helpers import session_decorator
from ..core import engine
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, desc


from error_handlers import (
    AddLastMessageError,
    GetLastMessageError,
)


@session_decorator(
    AddLastMessageError, "Ошибка при добавлении последнего сообщения в БД: "
)
def add_last_message(chat_id: int, text: str, message_id: int, session: Session):
    return add_last_message_impl(
        chat_id=chat_id, text=text, message_id=message_id, session=session
    )


def add_last_message_impl(chat_id: int, text: str, message_id: int, session: Session):

    response = delete(LastMessage).where(LastMessage.chat_id == chat_id)
    session.execute(response)

    last_message = LastMessage(chat_id=chat_id, text=text, message_id=message_id)
    session.add(last_message)
    session.commit()


@session_decorator(
    GetLastMessageError, "Ошибка при получении последнего сообщения из БД: "
)
def get_last_message(chat_id: int, session: Session):
    return get_last_message_impl(chat_id=chat_id, session=session)


def get_last_message_impl(chat_id: int, session: Session):
    response = (
        select(LastMessage)
        .where(LastMessage.chat_id == chat_id)
        .order_by(desc(LastMessage.id))
    )
    last_message = session.scalars(response).first()
    return last_message


def get_last_messages_impl(session: Session):
    response = select(LastMessage)
    last_message = session.scalars(response).all()
    return last_message
