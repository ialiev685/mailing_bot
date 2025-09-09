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
from typing import Any, Callable
import re


def has_value_in_data_name(value: str) -> Callable:
    def callback(query: Any) -> bool:
        if isinstance(query, types.CallbackQuery):
            return query.data and query.data.startswith(value)

        return False

    return callback


@bot.callback_query_handler(
    func=lambda call: call.data in [CallbackData.create_order.value]
)
def create_order(call: types.CallbackQuery):
    order = db.get_order_data_by_user_id(user_id=call.from_user.id)
    if order is None:
        db.create_order(user_id=call.from_user.id)

    if order:
        button_menu = None

        match order.current_step:
            case 1:
                button_menu = create_countries_button_menu(step=1)

            case 2:
                button_menu = create_days_button_menu(step=2)

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"*Шаг {order.current_step} из 2*\n\n Выберите направление:",
            parse_mode="Markdown",
            reply_markup=button_menu,
        )


@bot.callback_query_handler(func=has_value_in_data_name(PREFIX_COUNTRY))
@handler_error_decorator(func_name="handle_confirm_mailing")
def handle_choose_country(call: types.CallbackQuery):

    if call.data:
        response_by_step = re.search(r"{}(\d+)$".format(PREFIX_CURRENT_STEP), call.data)
        current_step = int(response_by_step.group(1)) if response_by_step else None

        order = db.get_order_data_by_user_id(user_id=call.from_user.id)
        if order.current_step == current_step:
            next_step = current_step + 1 if current_step else None
            response_by_country = re.search(
                r"{}([^_]+)-".format(PREFIX_COUNTRY), call.data
            )
            to_country = response_by_country.group(1) if response_by_country else None
            db.update_order_data_by_step(
                user_id=call.from_user.id, to_country=to_country, current_step=next_step
            )
            create_order(call=call)


@bot.callback_query_handler(func=has_value_in_data_name(PREFIX_DAYS))
@handler_error_decorator(func_name="handle_confirm_mailing")
def handle_choose_days(call: types.CallbackQuery):
    pass
