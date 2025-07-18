from ..models import LastMessage
from helpers import session_decorator
from ..core import engine
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, desc


from error_handlers import AddLastMessageError


@session_decorator(
    AddLastMessageError, "Ошибка при добавлении последнего сообщения в БД"
)
def add_last_message(chat_id: int, text: str, message_id: int, session: Session):

    # remove_last_message()

    last_message = LastMessage(chat_id=chat_id, text=text, message_id=message_id)
    session.add(last_message)
    session.commit()


def get_last_message():
    try:
        with Session(engine) as session:
            response = select(LastMessage).order_by(desc(LastMessage.id))
            last_message = session.scalars(response).first()

            return last_message

    except Exception as error:
        print("ahtung", error)
        raise


def remove_last_message():
    try:
        with Session(engine) as session:
            response = delete(LastMessage)
            session.execute(response)
            session.commit()

    except Exception as error:
        raise
