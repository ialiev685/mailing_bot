from database.models import StartMailingModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from helpers import session_decorator
from error_handlers import StartMailingError
from sqlalchemy.orm import Session


FLAG_NAME = "start_mailing"


@session_decorator(
    StartMailingError, "Ошибка при изменении флага в БД о начале рассылки: "
)
def update_flag_start_mailing(value: bool, session: Session):
    return update_flag_start_mailing_impl(value=value, session=session)


def update_flag_start_mailing_impl(value: bool, session: Session) -> StartMailingModel:
    response = select(StartMailingModel).where(StartMailingModel.name == FLAG_NAME)
    mailing_content = session.scalar(response)

    if mailing_content:
        mailing_content.value = value
    else:
        mailing_content = StartMailingModel(name=FLAG_NAME, value=value)
        session.add(mailing_content)

    session.commit()
    return mailing_content


@session_decorator(
    StartMailingError, "Ошибка при изменении флага в БД о начале рассылки: "
)
def get_start_mailing_data(session: Session) -> StartMailingModel | None:
    return get_start_mailing_data_impl(session=session)


def get_start_mailing_data_impl(session: Session) -> StartMailingModel | None:
    response = select(StartMailingModel).where(StartMailingModel.name == FLAG_NAME)
    mailing_content = session.scalar(response)
    return mailing_content
