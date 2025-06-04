import telebot
from telebot import types
from config import ADMIN_COMMANDS, USER_COMMANDS
from object_types import MailingContent
from dotenv import load_dotenv


import os
from pprint import pprint

load_dotenv(".env")


API_TOKEN = os.getenv("BOT_TOKEN", None)
ADMIN_ID = os.getenv("ADMIN_ID", None)

FORMATTED_ADMIN_IDS = ADMIN_ID.split(",") if ADMIN_ID else []


MAILING_CONTENT: list[MailingContent]


bot = telebot.TeleBot(API_TOKEN)


def is_admin(value: int):
    if str(value) in FORMATTED_ADMIN_IDS:
        return True
    return False


def set_menu_for_admin(chat_id: int):

    bot.set_my_commands(ADMIN_COMMANDS)
    bot.set_chat_menu_button(chat_id=chat_id, menu_button=types.MenuButtonCommands())


def set_menu_for_user(chat_id: int):

    bot.set_my_commands(ADMIN_COMMANDS)
    bot.set_chat_menu_button(chat_id=chat_id, menu_button=types.MenuButtonCommands())


@bot.message_handler(commands=["start"])
def subscribe(message: types.Message):

    if is_admin(message.from_user.id):
        set_menu_for_admin(chat_id=message.chat.id)
        bot.send_message(
            chat_id=message.chat.id, text=f"Привет 👋, {message.from_user.first_name}"
        )


@bot.message_handler(commands=["start_mailing"])
def start_mailing(message: types.Message):
    msg = bot.send_message(
        message.chat.id,
        "✍️ Вставьте сообщение (фото или текст, можно несколько) для рассылки.\n\n*Выполните команду /done когда закончите вставку необходимого контента.*",
        parse_mode="Markdown",
    )

    bot.register_next_step_handler(message=msg, callback=get_text_mailing)


def get_text_mailing(message: types.Message):
    content: MailingContent = {}
    if message.content_type == "photo":
        pass


bot.infinity_polling(restart_on_change=True)
