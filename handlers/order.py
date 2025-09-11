from bot_core import bot

from config import (
    CallbackData,
    create_countries_button_menu,
    create_days_button_menu,
    create_count_people_button_menu,
    create_month_button_menu,
    create_price_button_menu,
    create_social_network_button_menu,
    PREFIX_CURRENT_STEP,
    PREFIX_COUNTRY,
    PREFIX_DAYS,
    PREFIX_COUNT_PEOPLE,
    PREFIX_MONTH,
    PREFIX_PRICE,
    PREFIX_SOCIAL,
)
from telebot import types
import database.controllers as db
from helpers import handler_error_decorator
from typing import Any, Callable, TypedDict, Union
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
    step_6 = 6


class StepOptions(TypedDict):
    get_menu: Callable[[int], None]
    title: str


step_options: dict[int, StepOptions] = {
    Step.step_1.value: {
        "title": "Выберите направление для отдыха:",
        "get_menu": create_countries_button_menu,
    },
    Step.step_2.value: {
        "title": "На сколько дней планируете Ваш отдых?",
        "get_menu": create_days_button_menu,
    },
    Step.step_3.value: {
        "title": "Сколько человек отправится?",
        "get_menu": create_count_people_button_menu,
    },
    Step.step_4.value: {
        "title": "Выберите месяц для отпуска:",
        "get_menu": create_month_button_menu,
    },
    Step.step_5.value: {
        "title": "Выберите примерные бюджет:",
        "get_menu": create_price_button_menu,
    },
    Step.step_6.value: {
        "title": "Выберите как с вами связаться:",
        "get_menu": create_social_network_button_menu,
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
    bot.answer_callback_query(callback_query_id=call.id)
    order = db.get_order_data_by_user_id(user_id=call.from_user.id)
    if order is None:
        db.create_order(user_id=call.from_user.id)
    if order:
        count_steps = len(Step)

        if order.current_step <= count_steps:
            options = step_options[order.current_step]

            button_menu = options["get_menu"](order.current_step)

            bot.send_message(
                chat_id=call.message.chat.id,
                text=f"*Шаг {order.current_step} из {count_steps}*\n\n {options['title']}",
                parse_mode="Markdown",
                reply_markup=button_menu,
            )
        elif order.is_created_order:
            pass


def handle_step(call: types.CallbackQuery, prefix: str, field_name: FieldName):

    if call.data:
        bot.answer_callback_query(callback_query_id=call.id)
        current_step = get_step_number_from_button_data(call.data)
        order = db.get_order_data_by_user_id(user_id=call.from_user.id)

        if current_step and order.current_step == current_step:
            is_last_step = current_step == len(Step)
            next_step = current_step + 1 if current_step < len(Step) else current_step
            value = get_order_value_from_button_data(data=call.data, prefix=prefix)

            if value is None:
                return

            update_data: dict[FieldName, Union[str, int, None]] = {
                field_name: int(value) if value.isdigit() else value,
                "current_step": next_step,
                "is_created_order": is_last_step,
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


@bot.callback_query_handler(func=has_value_in_data_name(PREFIX_COUNT_PEOPLE))
@handler_error_decorator(func_name="handle_choose_count_people")
def handle_choose_count_people(call: types.CallbackQuery):
    return handle_step(call=call, prefix=PREFIX_COUNT_PEOPLE, field_name="count_people")


@bot.callback_query_handler(func=has_value_in_data_name(PREFIX_MONTH))
@handler_error_decorator(func_name="handle_choose_month")
def handle_choose_month(call: types.CallbackQuery):
    return handle_step(call=call, prefix=PREFIX_MONTH, field_name="month")


@bot.callback_query_handler(func=has_value_in_data_name(PREFIX_PRICE))
@handler_error_decorator(func_name="handle_choose_price")
def handle_choose_price(call: types.CallbackQuery):
    return handle_step(call=call, prefix=PREFIX_PRICE, field_name="price")


@bot.callback_query_handler(func=has_value_in_data_name(PREFIX_SOCIAL))
@handler_error_decorator(func_name="handle_choose_social_network")
def handle_choose_social_network(call: types.CallbackQuery):
    return handle_step(call=call, prefix=PREFIX_SOCIAL, field_name="connection")
