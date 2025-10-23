from bot_core import bot, bot_sender
from config import (
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
    CHAT_ID_FOR_SEND_ORDER,
    StepOptions,
    UsersCallbackData,
)
from telebot import types
import database.controllers as db
from database.models import OrderModel
from error_handlers import CreateOrderError
from helpers import (
    FAKE_CALL_ID,
    FakeCall,
    check_valid_phone,
    handler_error_decorator,
    has_value_in_data_name,
)
from typing import Union, TypedDict
import re


from object_types import FieldName


text_waiting_after_create_order = "Напишите в ответ на данное сообщение свой номер телефона, чтобы мы могли с вами связаться."


def get_step_number_from_button_data(data: str) -> int | None:
    response_by_step = re.search(r"{}(\d+)$".format(PREFIX_CURRENT_STEP), data)
    return int(response_by_step.group(1)) if response_by_step else None


def get_order_value_from_button_data(data: str, prefix: str) -> str | None:
    response_by_country = re.search(r"{}([^_]+)-".format(prefix), data)
    return response_by_country.group(1) if response_by_country else None


@bot.message_handler(
    content_types=["text"],
    func=lambda message: message.reply_to_message is not None
    and message.reply_to_message.from_user.is_bot
    and message.reply_to_message.text == text_waiting_after_create_order,
)
@handler_error_decorator(func_name="set_number_phone_after_create_order")
def set_number_phone_after_create_order(message: types.Message):
    if not message.from_user or not message.text:
        return

    order = db.get_order_data_by_user_id(user_id=message.from_user.id)

    if order and order.is_created_order and order.is_send_order:
        bot.send_message(
            chat_id=message.chat.id,
            text="✅ Заказ уже был отправлен ранее.",
            parse_mode="Markdown",
        )

    elif order and order.is_created_order and check_valid_phone(message.text):
        update_data: dict[FieldName, Union[str, int]] = {
            "user_id": message.from_user.id,
            "current_step": len(Step),
            "is_created_order": True,
            "phone": message.text,
            "is_send_order": True,
        }
        order_updated = db.update_order_data_by_step(**update_data)
        bot.send_message(
            chat_id=message.chat.id,
            text="🙏 Спасибо, мы скоро свяжеимся с вами.",
            parse_mode="Markdown",
        )

        formatted_order = {
            "Направление": order_updated.to_country,
            "Кол-во человек": order_updated.count_people,
            "Кол-во дней": order_updated.count_days,
            "Месяц отпуска": order_updated.month,
            "Бюджет": order_updated.price,
            "Отправить предложение": order_updated.connection,
            "Контактные данные": order_updated.phone,
        }

        order_details = "\n".join(
            [f"<b>{key}</b>: {value}" for key, value in formatted_order.items()]
        )

        bot_sender.send_message(
            chat_id=CHAT_ID_FOR_SEND_ORDER if CHAT_ID_FOR_SEND_ORDER else "",
            text=f"Вам заказ из телеграм-бота.\n\n{order_details}",
            parse_mode="HTML",
        )

    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="❌ Номер не валиден, попробуйте снова ввести номер",
            parse_mode="Markdown",
        )


def init_new_order(call: types.CallbackQuery):
    db.delete_order_data_by_user_id(user_id=call.from_user.id)
    db.create_order(user_id=call.from_user.id)


@bot.message_handler(commands=[CommandNames.order.value])
@handler_error_decorator(func_name="handle_begin_create_order")
def handle_begin_create_order(message: types.Message):
    fakeCall = FakeCall(message=message, data=UsersCallbackData.create_order.value)
    create_order(call=fakeCall)


class OrderStepOptions(TypedDict):
    count_steps: int
    options: StepOptions


def get_order_step_options_by_current_step(
    current_step: int,
) -> OrderStepOptions | None:
    count_steps = len(Step)
    if current_step <= count_steps:
        return {"count_steps": count_steps, "options": STEP_OPTIONS[current_step]}
    return None


def create_button_menu_for_order_step(call: types.CallbackQuery, order: OrderModel):
    if order.is_created_order is False:
        options = get_order_step_options_by_current_step(
            current_step=order.current_step
        )

        if options:
            button_menu = options["options"]["get_menu"](order.current_step)
            bot.send_message(
                chat_id=call.message.chat.id,
                text=f"*Шаг {order.current_step} из {options['count_steps']}*\n\n {options['options']['title']}",
                parse_mode="Markdown",
                reply_markup=button_menu,
            )

    elif order.is_created_order is True:
        bot.send_message(
            chat_id=call.message.chat.id,
            text=text_waiting_after_create_order,
            parse_mode="Markdown",
        )


@bot.callback_query_handler(
    func=lambda call: call.data in [UsersCallbackData.create_order.value]
    or call.data in [CommandNames.order.value]
)
@handler_error_decorator(func_name="create_order")
def create_order(
    call: types.CallbackQuery,
):
    if call.id != FAKE_CALL_ID:
        bot.answer_callback_query(callback_query_id=call.id)

    init_new_order(call=call)
    order = db.get_order_data_by_user_id(user_id=call.from_user.id)

    create_button_menu_for_order_step(call=call, order=order)


UpdateDataFromStep = dict[FieldName, Union[str, int, None]]


@handler_error_decorator(func_name="get_updated_data_from_current_step")
def get_updated_data_from_current_step(
    call: types.CallbackQuery, order: OrderModel, prefix: str, field_name: FieldName
) -> UpdateDataFromStep | None:
    if not call.data:
        return None
    current_step = get_step_number_from_button_data(call.data)
    if current_step and order.current_step == current_step:

        is_last_step = current_step == len(Step)
        next_step = current_step + 1 if current_step < len(Step) else current_step
        value = get_order_value_from_button_data(data=call.data, prefix=prefix)
        if value is None:
            return None

        update_data: UpdateDataFromStep = {
            "user_id": call.from_user.id,
            field_name: value,
            "current_step": next_step,
            "is_created_order": is_last_step,
            "is_send_order": False,
        }

        return update_data
    return None


def handle_step(call: types.CallbackQuery, prefix: str, field_name: FieldName):
    if call.data:
        bot.answer_callback_query(callback_query_id=call.id)
        order = db.get_order_data_by_user_id(user_id=call.from_user.id)
        if order.is_created_order:
            return
        updated_data = get_updated_data_from_current_step(
            call=call, order=order, prefix=prefix, field_name=field_name
        )
        if updated_data is None:
            raise CreateOrderError(
                message=f"Данные из кнопок под префиксом {prefix} пустые"
            )
        bot.delete_message(
            chat_id=call.message.chat.id, message_id=call.message.message_id
        )
        updated_order = db.update_order_data_by_step(**updated_data)
        create_button_menu_for_order_step(call=call, order=updated_order)


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
