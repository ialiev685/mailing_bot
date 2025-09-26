from database.models import AboutUs
from sqlalchemy.orm import Session
from helpers import session_decorator
from error_handlers import AdminAboutUsError
from sqlalchemy import select, delete


@session_decorator(AdminAboutUsError, "Ошибка при создании данных 'О нас': ")
def create_about_us_data(
    message_id: int, chat_id: int, file_id: str, caption: str, session: Session
) -> AboutUs:
    return create_about_us_data_impl(
        message_id=message_id,
        chat_id=chat_id,
        file_id=file_id,
        caption=caption,
        session=session,
    )


def create_about_us_data_impl(
    message_id: int, chat_id: int, file_id: str, caption: str, session: Session
) -> AboutUs:

    about_us = AboutUs(
        chat_id=chat_id, message_id=message_id, file_id=file_id, caption=caption
    )

    session.add(about_us)
    session.flush()
    session.execute(
        delete(AboutUs)
        .where(AboutUs.message_id != message_id)
        .where(AboutUs.chat_id == chat_id)
    )
    session.commit()
    session.refresh(about_us)
    return about_us


@session_decorator(AdminAboutUsError, "Ошибка при получении данных 'О нас': ")
def get_about_us_data(session: Session) -> AboutUs | None:
    return get_about_us_data_impl(session=session)


def get_about_us_data_impl(session: Session) -> AboutUs | None:
    query = select(AboutUs)
    about_us = session.scalar(query)
    return about_us
