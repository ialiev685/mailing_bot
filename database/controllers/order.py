from config import FORMATTED_ADMIN_IDS
from database.models import UserModel, SubscriberModel, RoleEnum, OrderModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, Union, TypedDict
from object_types import RoleEnum
from helpers import session_decorator
from error_handlers import CreateOrderError


class OrderFields(TypedDict, total=False):
    user_id: int
    current_step: int
    to_country: Optional[str]
    count_people: Optional[int]
    count_days: Optional[int]
    month: Optional[str]
    price: Optional[int]
    is_created_order: Optional[int]


@session_decorator(CreateOrderError, "Ошибка при создании подбора тура в БД: ")
def create_order(user_id: int, session: Session) -> Union[OrderModel, None]:
    return create_order_impl(user_id=user_id, session=session)


def create_order_impl(user_id: int, session: Session):
    order = OrderModel(user_id=user_id)
    session.add(order)
    session.commit()


@session_decorator(CreateOrderError, "Ошибка при обновлении подбора тура в БД: ")
def update_order_data_by_step(
    session: Session, **kwargs: OrderFields
) -> Union[OrderModel, None]:
    return update_order_data_by_step_impl(session=session, **kwargs)


def update_order_data_by_step_impl(
    session: Session, **kwargs: OrderFields
) -> Union[OrderModel, None]:
    response = select(OrderModel).where(OrderModel.user_id == kwargs["user_id"])
    order = session.scalar(response)
    if order:
        for key, value in kwargs.items():
            if value is not None:
                setattr(order, key, value)
        session.commit()
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
