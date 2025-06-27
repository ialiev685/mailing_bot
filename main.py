import telebot
from telebot import types
from config import (
    ADMIN_COMMANDS,
    USER_COMMANDS,
    CommandNames,
)
from object_types import MailingContentTypeModel, PhotoTypeModel
from dotenv import load_dotenv

from helpers import get_optimal_photo

from database.controllers import (
    create_user,
    get_user,
    subscribe_user,
    unsubscribe_user,
    add_content,
)


import os


load_dotenv(".env")


API_TOKEN = os.getenv("BOT_TOKEN", None)
ADMIN_ID = os.getenv("ADMIN_ID", None)
APP_PORT = os.getenv("APP_PORT", None)

FORMATTED_ADMIN_IDS = ADMIN_ID.split(",") if ADMIN_ID else []


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


@bot.message_handler(commands=[CommandNames.start.value])
def subscribe(message: types.Message):
    user = message.from_user

    user_subscriber = get_user(user.id)

    if user_subscriber is None:
        create_user(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            chat_id=message.chat.id,
        )
    else:
        subscribe_user(user.id)

    if is_admin(message.from_user.id):

        set_menu_for_admin(chat_id=message.chat.id)

        bot.send_message(
            chat_id=message.chat.id,
            text=f"Привет 👋, {message.from_user.first_name} {message.from_user.last_name}",
            parse_mode="Markdown",
        )
    else:
        set_menu_for_user(chat_id=message.chat.id)

        bot.send_message(
            chat_id=message.chat.id,
            text=f"Привет 👋, {message.from_user.first_name} {message.from_user.last_name}",
            parse_mode="Markdown",
        )


@bot.message_handler(commands=[CommandNames.stop.value])
def unsubscribe(message: types.Message):
    subscriber = unsubscribe_user(message.from_user.id)

    if subscriber is not None and subscriber.signed is False:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Вы отписались 😢",
            parse_mode="Markdown",
        )


@bot.message_handler(commands=[CommandNames.start_mailing.value])
def start_mailing(message: types.Message):

    msg = bot.send_message(
        chat_id=message.chat.id,
        text=f"✍️ Вставьте сообщение (фото или текст, можно несколько) для рассылки.\n\n*Выполните команду {CommandNames.done.value} когда закончите вставку необходимого контента.*",
        parse_mode="Markdown",
    )

    bot.register_next_step_handler(message=msg, callback=get_text_mailing)


def get_text_mailing(message: types.Message):
    try:
        if message.text == CommandNames.done.value:
            confirm_mailing(message.chat.id)
            return

        photo = get_optimal_photo(message.photo)

        content = MailingContentTypeModel(
            content_type=message.content_type,
            text=message.text,
            photo=(
                PhotoTypeModel(
                    file_id=photo.file_id, width=photo.width, height=photo.height
                )
                if photo is not None
                else None
            ),
        )

        add_content(content)

        msg = bot.send_message(
            chat_id=message.chat.id,
            text=f"✅ Сообщение добавлено. *Отправьте еще или нажмите {CommandNames.done.value} для завершения.*",
            parse_mode="Markdown",
        )

        bot.register_next_step_handler(message=msg, callback=get_text_mailing)
    except Exception as error:
        print("Ошибка слушателя для вставки контента: ", error)
        msg = bot.send_message(
            chat_id=message.chat.id,
            text="⚠️ Произошла ошибка при обработке сообщения. Пожалуйста, попробуйте еще раз.",
            parse_mode="Markdown",
        )

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

    if call.data == "cancel_mailing":
        print("Нажали нет")
        bot.send_message(chat_id=call.message.id, text="❌ Вы отменили рассылку.")


if __name__ == "__main__":
    try:
        bot.infinity_polling(restart_on_change=True)
    except Exception as error:
        print("error by start server:", error)
