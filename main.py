import telebot
from telebot import types
from config import (
    ADMIN_COMMANDS,
    USER_COMMANDS,
    CommandNames,
)
from object_types import (
    RoleEnum,
)
from dotenv import load_dotenv
from time import sleep
from helpers import get_formatted_content, create_media_group
from error_handlers import (
    AddMailingContentError,
    CheckMailingContentError,
    GetMailingContentError,
    RemoveMailingContentError,
)

import database.controllers as db

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


def send_message_without_duplicates(
    chat_id: int, message_from_chat: str, send_text: str
):

    last_message = db.get_last_message()

    if (
        last_message is not None
        and last_message.chat_id == chat_id
        and last_message.text == message_from_chat
    ):

        return

    db.add_last_message(chat_id=chat_id, text=send_text)

    bot.send_message(
        chat_id=chat_id,
        text=send_text,
        parse_mode="Markdown",
    )


def send_message_about_mailing_error(chat_id: int):
    bot.send_message(
        chat_id=chat_id,
        text="⚠️ Произошла ошибка при обработке сообщения. Запустите рассылку заново.",
        parse_mode="Markdown",
    )

    db.remove_content()


@bot.message_handler(commands=[CommandNames.start.value])
def subscribe(message: types.Message):

    user = message.from_user

    user_subscriber = db.get_user(user.id)

    is_admin_user = is_admin(message.from_user.id)

    role = RoleEnum.ADMIN if is_admin_user else RoleEnum.USER

    if user_subscriber is None:
        db.create_user(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            chat_id=message.chat.id,
            role=role,
        )
    else:
        db.subscribe_user(user.id)

    if is_admin(message.from_user.id):

        set_menu_for_admin(chat_id=message.chat.id)

    else:
        set_menu_for_user(chat_id=message.chat.id)

    send_message_without_duplicates(
        chat_id=message.chat.id,
        send_text=f"Привет 👋, {message.from_user.first_name} {message.from_user.last_name}",
        message_from_chat=message.text,
    )


@bot.message_handler(commands=[CommandNames.stop.value])
def unsubscribe(message: types.Message):
    subscriber = db.unsubscribe_user(message.from_user.id)

    if subscriber is not None and subscriber.signed is False:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Вы отписались 😢",
            parse_mode="Markdown",
        )


@bot.message_handler(commands=[CommandNames.start_mailing.value])
def start_mailing(message: types.Message):
    db.remove_content()
    msg = bot.send_message(
        chat_id=message.chat.id,
        text=f"✍️ Вставьте сообщение (фото или текст, можно несколько) для рассылки.\n\n*Выполните команду /{CommandNames.done.value} когда закончите вставку необходимого контента.*",
        parse_mode="Markdown",
    )

    bot.register_next_step_handler(message=msg, callback=get_text_mailing)


@bot.message_handler(content_types=["text", "photo", "video"])
def get_text_mailing(message: types.Message):

    try:
        if message.text == f"/{CommandNames.done.value}":

            if db.check_content() == False:
                msg = bot.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ У вас нет сообщений для рассылки.",
                    parse_mode="Markdown",
                )
                return

            confirm_mailing(message.chat.id)
            return

        content = get_formatted_content(message)

        if content is not None:
            db.add_mailing_content(content)

        msg = bot.send_message(
            chat_id=message.chat.id,
            text=f"✅ Сообщение добавлено. *Отправьте еще или нажмите /{CommandNames.done.value} для завершения.*",
            parse_mode="Markdown",
        )

        bot.register_next_step_handler(message=msg, callback=get_text_mailing)
    except CheckMailingContentError as error:
        send_message_about_mailing_error(message.chat.id)
    except AddMailingContentError as error:
        send_message_about_mailing_error(message.chat.id)
    except Exception as error:
        send_message_about_mailing_error(message.chat.id)


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
    try:

        bot.delete_message(
            chat_id=call.message.chat.id, message_id=call.message.message_id
        )

        if call.data == "confirm_mailing":

            users = db.get_users()

            sorted_single_content, sorted_group_content = db.get_mailing_content()

            for uses in users:
                for content in sorted_single_content:
                    if content.content_type == "text":
                        bot.send_message(
                            chat_id=uses.chat_id,
                            text=content.text,
                            parse_mode="Markdown",
                        )
                    if content.content_type == "photo":
                        bot.send_photo(
                            chat_id=uses.chat_id,
                            caption=content.caption,
                            photo=content.file_id,
                            parse_mode="Markdown",
                        )

                    sleep(0.3)
                for key, content in sorted_group_content.items():
                    if len(content) > 0 and content[0].content_type == "photo":
                        media = create_media_group(content, types.InputMediaPhoto)
                        bot.send_media_group(chat_id=uses.chat_id, media=media)
                    if len(content) > 0 and content[0].content_type == "video":
                        media = create_media_group(content, types.InputMediaVideo)
                        bot.send_media_group(chat_id=uses.chat_id, media=media)
                    sleep(0.3)

            db.remove_content()
    except Exception as error:
        print("error", error)

        if call.data == "cancel_mailing":
            db.remove_content()
            bot.send_message(chat_id=call.message.id, text="❌ Вы отменили рассылку.")


if __name__ == "__main__":
    try:
        bot.infinity_polling(restart_on_change=True)
    except Exception as error:
        print("error by start server:", error)
