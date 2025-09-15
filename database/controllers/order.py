from database.models import OrderModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Union
from object_types import OrderFieldsTypeModel
from helpers import session_decorator
from error_handlers import CreateOrderError
from pydantic import ValidationError


@session_decorator(CreateOrderError, "Ошибка при создании подбора тура в БД: ")
def create_order(user_id: int, session: Session) -> OrderModel:
    return create_order_impl(user_id=user_id, session=session)


def create_order_impl(user_id: int, session: Session) -> OrderModel:
    order = OrderModel(user_id=user_id)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@session_decorator(CreateOrderError, "Ошибка при обновлении подбора тура в БД: ")
def update_order_data_by_step(session: Session, **kwargs) -> Union[OrderModel, None]:
    return update_order_data_by_step_impl(session=session, **kwargs)


def update_order_data_by_step_impl(
    session: Session, **kwargs
) -> Union[OrderModel, None]:

    response = select(OrderModel).where(OrderModel.user_id == kwargs["user_id"])
    order = session.scalar(response)

    if order:
        try:

            fields = OrderFieldsTypeModel.model_validate(kwargs).model_dump(
                exclude_none=True
            )

            for key, value in fields.items():
                if value is not None:
                    setattr(order, key, value)
            session.commit()
        except ValidationError as error:
            raise CreateOrderError(
                "Ошибка при валидации данных во вреия обновления данных заказа в БД:",
                error,
            )

    return order


@session_decorator(
    CreateOrderError, "Ошибка при получении текущего шага подбора тура из БД: "
)
def get_order_data_by_user_id(
    user_id: int, session: Session
) -> Union[OrderModel, None]:
    return get_order_data_by_user_id_impl(user_id=user_id, session=session)


def get_order_data_by_user_id_impl(
    user_id: int, session: Session
) -> Union[OrderModel, None]:
    response = select(OrderModel).where(OrderModel.user_id == user_id)
    order = session.scalar(response)
    return order


@session_decorator(CreateOrderError, "Ошибка при удалении подбора тура из БД: ")
def delete_order_data_by_user_id(
    user_id: int, session: Session
) -> Union[OrderModel, None]:
    return delete_order_data_by_user_id_impl(user_id=user_id, session=session)


def delete_order_data_by_user_id_impl(user_id: int, session: Session):
    response = select(OrderModel).where(OrderModel.user_id == user_id)
    order = session.scalar(response)
    if order is not None:
        session.delete(order)
        session.commit()
