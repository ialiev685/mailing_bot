from database.models import AboutUs
from sqlalchemy.orm import Session
from helpers import session_decorator
from error_handlers import AdminAboutUsError
from sqlalchemy import select, delete


@session_decorator(AdminAboutUsError, "Ошибка при создании данных 'О нас': ")
def create_about_us_data(message_id: int, chat_id: int, session: Session) -> AboutUs:
    return create_about_us_data_impl(
        message_id=message_id, chat_id=chat_id, session=session
    )


def create_about_us_data_impl(
    message_id: int, chat_id: int, session: Session
) -> AboutUs:

    about_us = AboutUs(chat_id=chat_id, message_id=message_id)
    session.add(about_us)
    session.commit()
    session.refresh(about_us)
    return about_us


@session_decorator(AdminAboutUsError, "Ошибка при обновлении данных 'О нас': ")
def update_about_us_data(
    message_id: int, chat_id: int, file_id: str, session: Session
) -> AboutUs | None:
    return update_about_us_data_impl(
        message_id=message_id, chat_id=chat_id, file_id=file_id, session=session
    )


def update_about_us_data_impl(
    message_id: int, chat_id: int, file_id: str, session: Session
) -> AboutUs | None:

    response = (
        select(AboutUs)
        .where(AboutUs.chat_id == chat_id)
        .where(AboutUs.message_id == message_id)
        .where(AboutUs.is_draft == True)
    )
    about_us = session.scalar(response)
    if about_us:
        about_us.file_id = file_id
        session.commit()

    return about_us


@session_decorator(AdminAboutUsError, "Ошибка при удалении данных 'О нас': ")
def remove_draft_about_us_data(session: Session) -> AboutUs | None:
    return remove_draft_about_us_data_impl(session=session)


def remove_draft_about_us_data_impl(session: Session):
    response = delete(AboutUs).where(AboutUs.is_draft == True)
    session.execute(response)
    session.commit()
