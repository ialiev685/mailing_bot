from database.models import AboutUs
from sqlalchemy.orm import Session
from helpers import session_decorator
from error_handlers import AdminAboutUsError
from sqlalchemy import select, delete, update
from object_types import StatusAboutUsContent


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
    session.commit()
    session.refresh(about_us)
    return about_us


@session_decorator(AdminAboutUsError, "Ошибка при обновлении данных 'О нас': ")
def update_about_us_data(
    message_id: int, chat_id: int, session: Session
) -> AboutUs | None:
    return update_about_us_data_impl(
        message_id=message_id,
        chat_id=chat_id,
        session=session,
    )


def update_about_us_data_impl(
    message_id: int, chat_id: int, session: Session
) -> AboutUs | None:
    query = select(AboutUs).where(AboutUs.chat_id == chat_id)
    about_us = session.scalars(query)

    updated_about_us = None

    for item in about_us:
        if item.message_id == message_id:
            item.status = StatusAboutUsContent.ACTIVE
            updated_about_us = item
        else:
            item.status = StatusAboutUsContent.DRAFT

    session.commit()
    if updated_about_us:
        session.refresh(updated_about_us)
    return updated_about_us


@session_decorator(AdminAboutUsError, "Ошибка при обновлении данных 'О нас': ")
def remove_about_us_data(chat_id: int, session: Session) -> AboutUs | None:
    return remove_about_us_data_impl(
        chat_id=chat_id,
        session=session,
    )


def remove_about_us_data_impl(chat_id: int, session: Session):
    query = (
        delete(AboutUs)
        .where(AboutUs.chat_id == chat_id)
        .where(AboutUs.status == StatusAboutUsContent.DRAFT)
    )
    session.execute(query)
    session.commit()


@session_decorator(AdminAboutUsError, "Ошибка при получении данных 'О нас': ")
def get_about_us_data(session: Session) -> AboutUs | None:
    return get_about_us_data_impl(session=session)


def get_about_us_data_impl(session: Session) -> AboutUs | None:
    query = select(AboutUs).where(AboutUs.status == StatusAboutUsContent.ACTIVE)
    about_us = session.scalar(query)
    return about_us
