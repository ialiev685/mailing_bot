from bot_core import bot
from config import (
    CallbackData,
    PREFIX_CURRENT_STEP,
    PREFIX_COUNTRY,
    PREFIX_DAYS,
    PREFIX_COUNT_PEOPLE,
    PREFIX_MONTH,
    PREFIX_PRICE,
    PREFIX_SOCIAL,
    Step,
    STEP_OPTIONS,
    CommandNames,
)
from telebot import types
import database.controllers as db
from helpers import handler_error_decorator
from typing import Any, Callable, TypedDict, Union
import re

from object_types import FieldName


def has_value_in_data_name(value: str) -> Callable:
    def callback(query: Any) -> bool:
        if isinstance(query, types.CallbackQuery):
            return query.data and query.data.startswith(value)

        return False

    return callback


def get_step_number_from_button_data(data: str) -> int | None:
    response_by_step = re.search(r"{}(\d+)$".format(PREFIX_CURRENT_STEP), data)
    return int(response_by_step.group(1)) if response_by_step else None


def get_order_value_from_button_data(data: str, prefix: str) -> str | None:
    response_by_country = re.search(r"{}([^_]+)-".format(prefix), data)
    return response_by_country.group(1) if response_by_country else None


def handle_phone(message: types.Message):
    if message.content_type == "text" and message.text:
        is_valid_phone = re.match(
            r"^(\+7|7|8)?[\s\-\(\)]*9\d{2}[\s\-\(\)]*\d{3}[\s\-\(\)]*\d{2}[\s\-\(\)]*\d{2}$",
            message.text,
        )
        if is_valid_phone:
            update_data: dict[FieldName, Union[str, int, None]] = {
                "user_id": message.from_user.id,
                "current_step": len(Step),
                "is_created_order": True,
                "phone": message.text,
            }
            db.update_order_data_by_step(**update_data)
            bot.send_message(
                chat_id=message.chat.id,
                text="🙏 Спасибо, мы скоро свяжеимся с вами.",
                parse_mode="Markdown",
            )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="❌ Номер не валиден, попробуйте снова ввести номер",
                parse_mode="Markdown",
            )
            bot.register_next_step_handler(message=message, callback=handle_phone)


def init_new_order(call: types.CallbackQuery):
    db.delete_order_data_by_user_id(user_id=call.from_user.id)
    db.create_order(user_id=call.from_user.id)


@bot.message_handler(commands=[CommandNames.order.value])
@handler_error_decorator(func_name="handle_unsubscribe")
def handle_begin_create_order(message: types.Message):

    # имитация вызова кнопки
    class FakeCall:
        def __init__(self, message: types.Message):
            self.id = "fake_call_id"
            self.message = message
            self.data = CallbackData.create_order
            self.from_user = message.from_user

    fakeCall = FakeCall(message=message)

    create_order(call=fakeCall)


@bot.callback_query_handler(
    func=lambda call: call.data in [CallbackData.create_order.value]
)
@handler_error_decorator(func_name="create_order")
def create_order(call: types.CallbackQuery, is_next_step: bool = False):
    if not isinstance(call.id, str):
        bot.answer_callback_query(callback_query_id=call.id)
    if is_next_step is False:
        init_new_order(call=call)
    order = db.get_order_data_by_user_id(user_id=call.from_user.id)

    if order.is_created_order is False:
        count_steps = len(Step)

        if order.current_step <= count_steps:
            options = STEP_OPTIONS[order.current_step]

            button_menu = options["get_menu"](order.current_step)

            bot.send_message(
                chat_id=call.message.chat.id,
                text=f"*Шаг {order.current_step} из {count_steps}*\n\n {options['title']}",
                parse_mode="Markdown",
                reply_markup=button_menu,
            )
    elif order.is_created_order is True:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Напишите после данного сообщения свой номер телефона, чтобы мы могли с вами связать.",
            parse_mode="Markdown",
        )
        bot.register_next_step_handler(message=call.message, callback=handle_phone)


def handle_step(call: types.CallbackQuery, prefix: str, field_name: FieldName):

    if call.data:
        bot.answer_callback_query(callback_query_id=call.id)
        order = db.get_order_data_by_user_id(user_id=call.from_user.id)
        if order.is_created_order:
            return
        current_step = get_step_number_from_button_data(call.data)

        if current_step and order.current_step == current_step:
            is_last_step = current_step == len(Step)
            next_step = current_step + 1 if current_step < len(Step) else current_step
            value = get_order_value_from_button_data(data=call.data, prefix=prefix)

            if value is None:
                return

            update_data: dict[FieldName, Union[str, int, None]] = {
                "user_id": call.from_user.id,
                field_name: value,
                "current_step": next_step,
                "is_created_order": is_last_step,
            }

            db.update_order_data_by_step(**update_data)
            create_order(call=call, is_next_step=True)


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
