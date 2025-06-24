import telebot
from telebot import types
from config import ADMIN_COMMANDS, USER_COMMANDS, COMPLETE_EDIT_CONFIRM
from object_types import MailingContent
from dotenv import load_dotenv

from database.controllers import create_user


import os
from pprint import pprint

load_dotenv(".env")


API_TOKEN = os.getenv("BOT_TOKEN", None)
ADMIN_ID = os.getenv("ADMIN_ID", None)
APP_PORT = os.getenv("APP_PORT", None)

FORMATTED_ADMIN_IDS = ADMIN_ID.split(",") if ADMIN_ID else []


MAILING_CONTENT: list[MailingContent] = []


bot = telebot.TeleBot(API_TOKEN)


def is_admin(value: int):
    if str(value) in FORMATTED_ADMIN_IDS:
        return True
    return False


def set_menu_for_admin(chat_id: int):

    bot.set_my_commands(ADMIN_COMMANDS)
    bot.set_chat_menu_button(chat_id=chat_id, menu_button=types.MenuButtonCommands())


def set_menu_for_user(chat_id: int):

    bot.set_my_commands(USER_COMMANDS)
    bot.set_chat_menu_button(chat_id=chat_id, menu_button=types.MenuButtonCommands())


@bot.message_handler(commands=["start"])
def subscribe(message: types.Message):

    if is_admin(message.from_user.id):
        user = message.from_user

        create_user(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            chat_id=message.chat.id,
        )

        set_menu_for_admin(chat_id=message.chat.id)

        bot.send_message(
            chat_id=message.chat.id,
            text=f"Привет 👋, {message.from_user.first_name}",
            parse_mode="Markdown",
        )
    else:
        set_menu_for_user(chat_id=message.chat.id)


@bot.message_handler(commands=["start_mailing"])
def start_mailing(message: types.Message):
    MAILING_CONTENT.clear()

    msg = bot.send_message(
        chat_id=message.chat.id,
        text=f"✍️ Вставьте сообщение (фото или текст, можно несколько) для рассылки.\n\n*Выполните команду {COMPLETE_EDIT_CONFIRM} когда закончите вставку необходимого контента.*",
        parse_mode="Markdown",
    )

    bot.register_next_step_handler(message=msg, callback=get_text_mailing)


def get_text_mailing(message: types.Message):

    if message.text == COMPLETE_EDIT_CONFIRM:
        confirm_mailing(message.chat.id)
        return

    content = MailingContent(content_type=message.content_type, text=None, photo=None)

    msg = bot.send_message(
        chat_id=message.chat.id,
        text=f"✅ Сообщение добавлено. *Отправьте еще или нажмите {COMPLETE_EDIT_CONFIRM} для завершения.*",
        parse_mode="Markdown",
    )
    if message.content_type == "photo":
        if len(message.photo) >= 3:
            content.photo = message.photo[2]
        else:
            content.photo = message.photo

    if message.content_type == "text":
        content.text = message.text

    MAILING_CONTENT.append(content)

    bot.register_next_step_handler(message=msg, callback=get_text_mailing)


def confirm_mailing(chat_id: int):
    markup_object = types.InlineKeyboardMarkup()
    button_confirm = types.InlineKeyboardButton(
        text="✅ Отправить", callback_data="confirm_mailing"
    )
    button_cancel = types.InlineKeyboardButton(
        text="❌ Отмена", callback_data="cancel_mailing"
    )
    markup_object.add(button_confirm, button_cancel)

    bot.send_message(
        chat_id=chat_id,
        text="🚀 Вы действительно хотите выполнить рассылку?",
        parse_mode="Markdown",
        reply_markup=markup_object,
    )


@bot.callback_query_handler(
    func=lambda call: call.data in ["confirm_mailing", "cancel_mailing"]
)
def handle_confirm_mailing(call: types.CallbackQuery):
    if call.data == "confirm_mailing":
        print("Нажали да")
        print("контент", MAILING_CONTENT)
    if call.data == "cancel_mailing":
        print("Нажали нет")
        bot.send_message(chat_id=call.message.id, text="❌ Вы отменили рассылку.")


if __name__ == "__main__":
    try:
        bot.infinity_polling(restart_on_change=True)
    except Exception as error:
        print("error by start server:", error)
