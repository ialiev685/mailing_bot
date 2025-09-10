from bot_core import bot

from config import (
    CallbackData,
    create_countries_button_menu,
    create_days_button_menu,
    PREFIX_CURRENT_STEP,
    PREFIX_COUNTRY,
    PREFIX_DAYS,
)
from telebot import types
import database.controllers as db
from helpers import handler_error_decorator
from typing import Any, Callable, Literal, TypedDict, Union
import re
from enum import Enum
from object_types import FieldName


def has_value_in_data_name(value: str) -> Callable:
    def callback(query: Any) -> bool:
        if isinstance(query, types.CallbackQuery):
            return query.data and query.data.startswith(value)

        return False

    return callback


class Step(Enum):
    step_1 = 1
    step_2 = 2
    step_3 = 3
    step_4 = 4
    step_5 = 5


class StepOptions(TypedDict):
    get_menu: Callable[[int], None]
    title: str


step_options: dict[int, StepOptions] = {
    Step.step_1.value: {
        "title": "Выберите направление:",
        "get_menu": create_countries_button_menu,
    },
    Step.step_2.value: {
        "title": "Выберите количество дней:",
        "get_menu": create_days_button_menu,
    },
}


def get_step_number_from_button_data(data: str) -> int | None:
    response_by_step = re.search(r"{}(\d+)$".format(PREFIX_CURRENT_STEP), data)
    return int(response_by_step.group(1)) if response_by_step else None


def get_order_value_from_button_data(data: str, prefix: str) -> str | None:
    response_by_country = re.search(r"{}([^_]+)-".format(prefix), data)
    return response_by_country.group(1) if response_by_country else None


@bot.callback_query_handler(
    func=lambda call: call.data in [CallbackData.create_order.value]
)
@handler_error_decorator(func_name="create_order")
def create_order(call: types.CallbackQuery):
    order = db.get_order_data_by_user_id(user_id=call.from_user.id)
    if order is None:
        db.create_order(user_id=call.from_user.id)

    if order:
        options = step_options[order.current_step]
        button_menu = options["get_menu"](order.current_step)
        count_steps = len(Step)

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"*Шаг {order.current_step} из {count_steps}*\n\n {options['title']}",
            parse_mode="Markdown",
            reply_markup=button_menu,
        )


def handle_step(call: types.CallbackQuery, prefix: str, field_name: FieldName):
    if call.data:
        current_step = get_step_number_from_button_data(call.data)
        order = db.get_order_data_by_user_id(user_id=call.from_user.id)

        if current_step and order.current_step == current_step:
            next_step = current_step + 1
            value = get_order_value_from_button_data(data=call.data, prefix=prefix)

            if value is None:
                return

            update_data: dict[FieldName, Union[str, int, None]] = {
                field_name: int(value) if value.isdigit() else value,
                "current_step": next_step,
            }

            db.update_order_data_by_step(user_id=call.from_user.id, **update_data)
            create_order(call=call)


@bot.callback_query_handler(func=has_value_in_data_name(PREFIX_COUNTRY))
@handler_error_decorator(func_name="handle_choose_country")
def handle_choose_country(call: types.CallbackQuery):
    return handle_step(call=call, prefix=PREFIX_COUNTRY, field_name="to_country")


@bot.callback_query_handler(func=has_value_in_data_name(PREFIX_DAYS))
@handler_error_decorator(func_name="handle_choose_days")
def handle_choose_days(call: types.CallbackQuery):
    return handle_step(call=call, prefix=PREFIX_DAYS, field_name="count_days")
