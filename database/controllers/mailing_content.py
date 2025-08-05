from ..models import MailingContentModel
from helpers import parse_and_sort_content
from ..core import engine
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, exists
from helpers import session_decorator
from object_types import MailingContentType
from error_handlers import (
    AddMailingContentError,
    CheckMailingContentError,
    GetMailingContentError,
    RemoveMailingContentError,
)
from sqlalchemy.orm import Session


@session_decorator(AddMailingContentError, "Ошибка при добавлении контента в БД: ")
def add_mailing_content(content_data: MailingContentType, session: Session):
    return add_mailing_content_impl(content_data=content_data, session=session)


def add_mailing_content_impl(content_data: MailingContentType, session: Session):
    mailing_content = MailingContentModel(content=content_data.model_dump_json())
    session.add(mailing_content)
    session.commit()
    return mailing_content


@session_decorator(
    CheckMailingContentError, "Ошибка при проверке наличия контента в БД: "
)
def check_content(session: Session) -> bool:
    return check_content_impl(session=session)


def check_content_impl(session: Session) -> bool:
    response = select(exists().select_from(MailingContentModel))
    has_content = bool(session.scalar(response))
    return has_content


@session_decorator(GetMailingContentError, "Ошибка при получения контента из БД: ")
def get_mailing_content(session: Session):
    return get_mailing_content_impl(session=session)


def get_mailing_content_impl(session: Session):
    response = select(MailingContentModel)
    content = session.scalars(response).all()
    return parse_and_sort_content(list(content))


@session_decorator(RemoveMailingContentError, "Ошибка при очистке контента в БД: ")
def remove_content(session: Session):
    return remove_content_impl(session=session)


def remove_content_impl(session: Session):
    response = delete(MailingContentModel)
    session.execute(response)
    session.commit()
