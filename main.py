import logging

from bot_core import bot
from handlers.mailing import *
from handlers.order import *
from handlers.admin import *


from telebot import types
from config import CommandNames, CallbackData, USER_COMMANDS, BOT_NAME
from object_types import RoleEnum


from helpers import handler_error_decorator

import database.controllers as db
from bot_core import bot


def create_shared_menu() -> types.InlineKeyboardMarkup:
    markup_object = types.InlineKeyboardMarkup()
    button_create_order = types.InlineKeyboardButton(
        text="✈️ Подобрать тур", callback_data=CallbackData.create_order.value
    )
    button_link_to_site = types.InlineKeyboardButton(
        text="✍️ Cвое предложение",
        callback_data=CallbackData.link_to_site.value,
        url="https://www.all-inc-travel-online.ru",
    )
    button_about = types.InlineKeyboardButton(
        text="💬 О нас", callback_data=CallbackData.about.value
    )
    markup_object.add(button_create_order)
    markup_object.add(button_link_to_site)
    markup_object.add(button_about)
    return markup_object


@bot.message_handler(commands=[CommandNames.start.value])
@handler_error_decorator(func_name="handle_subscribe")
def handle_subscribe(message: types.Message):

    user = message.from_user
    user_subscriber = db.get_user(user.id)
    is_admin_user = is_admin(user_id=message.from_user.id)
    role = RoleEnum.ADMIN if is_admin_user else RoleEnum.USER

    if user_subscriber is None:
        db.create_user(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            chat_id=message.chat.id,
            role=role,
        )

    bot.set_my_commands(commands=USER_COMMANDS)

    markup_object = create_shared_menu()

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Добрый день 👋, {message.from_user.first_name}. \n\nМеня завут {BOT_NAME}. Я являюсь менеджером турагенства 'Ол Инклюзив' и помогу Вам организовать ваш лучший отдых. \n\n Выберите подходящий пукт меню чтобы подобрать тур",
        parse_mode="Markdown",
        reply_markup=markup_object,
    )


def init_logger_config():
    logging.basicConfig(
        filename="logs.log",
        level=logging.INFO,
        format="%(asctime)s - %(filename)s - row:%(lineno)s - %(levelname)s - %(message)s - callback name:%(func_name)s",
    )


if __name__ == "__main__":
    while True:
        try:

            init_logger_config()
            bot.infinity_polling(restart_on_change=True)
            # bot.infinity_polling()

        except Exception as error:
            print("error by start server:", error)
