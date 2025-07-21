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
from typing import Union
from dotenv import load_dotenv
from time import sleep
from helpers import get_formatted_content, create_media_group
from error_handlers import (
    AddMailingContentError,
    CheckMailingContentError,
    GetMailingContentError,
    RemoveMailingContentError,
    RemoveLastMessageError,
)
import requests
import database.controllers as db
from threading import Lock
import os

lock = Lock()

load_dotenv(".env")
# https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/getMe

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


def get_and_send_message_without_duplicates(
    chat_id: int, send_text: str, reply_markup: types.InlineKeyboardMarkup = None
) -> Union[types.Message, None]:

    last_message = db.get_last_message()

    try:

        if (
            last_message
            and last_message.chat_id == chat_id
            and last_message.text == send_text
            and last_message.message_id
        ):

            bot.delete_message(
                chat_id=last_message.chat_id, message_id=last_message.message_id
            )
    except Exception as error:
        print("error message", last_message.message_id)
        raise RemoveLastMessageError("Ошибка при удалении последнего сообщения", error)

    msg = bot.send_message(
        chat_id=chat_id,
        text=send_text,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

    db.add_last_message(chat_id=chat_id, text=send_text, message_id=msg.message_id)

    return msg


def send_message_about_mailing_error(chat_id: int):
    get_and_send_message_without_duplicates(
        chat_id=chat_id,
        send_text="⚠️ Произошла ошибка при обработке сообщения. Запустите рассылку заново.",
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

    get_and_send_message_without_duplicates(
        chat_id=message.chat.id,
        send_text=f"Привет 👋, {message.from_user.first_name} {message.from_user.last_name}",
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

    msg = get_and_send_message_without_duplicates(
        chat_id=message.chat.id,
        send_text=f"✍️ Вставьте сообщение (фото или текст, можно несколько) для рассылки.\n\n*Выполните команду /{CommandNames.done.value} когда закончите вставку необходимого контента.*",
    )

    bot.register_next_step_handler(message=msg, callback=get_text_mailing)


@bot.message_handler(content_types=["text", "photo", "video"])
def get_text_mailing(message: types.Message):
    try:
        # Плокируем поток - останавливаем выполнение паралельных функций
        # При отправке нескольких файлов, хэндер срабатывает по количеству файлов.
        # Вызывы срабатывают паральено в разных потоках, из-чего обращаются к БД одновременно по одинаковому id.
        # В данном случае удалению по одинакову id вызвает ошибку т к одна из-за вызванных функций произвела удаление.
        lock.acquire()
        if message.text == f"/{CommandNames.done.value}":

            if db.check_content() == False:
                get_and_send_message_without_duplicates(
                    chat_id=message.chat.id,
                    send_text=f"❌ У вас нет сообщений для рассылки.",
                )
                return

            confirm_mailing(message.chat.id)
            return
        if message.text == f"/{CommandNames.start_mailing.value}":
            start_mailing(message=message)
            return

        content = get_formatted_content(message)

        if content is not None:
            db.add_mailing_content(content)

        msg = get_and_send_message_without_duplicates(
            chat_id=message.chat.id,
            send_text=f"✅ Сообщение добавлено. *Отправьте еще или нажмите /{CommandNames.done.value} для завершения.*",
        )

        bot.register_next_step_handler(message=msg, callback=get_text_mailing)
    except CheckMailingContentError as error:
        print(error)
        send_message_about_mailing_error(message.chat.id)
    except AddMailingContentError as error:
        print(error)
        send_message_about_mailing_error(message.chat.id)
    except RemoveLastMessageError as error:
        print(error)
        send_message_about_mailing_error(message.chat.id)
    except Exception as error:
        print(error)
        send_message_about_mailing_error(message.chat.id)
    finally:
        # После завершения функции, отпускаем блокировку потока
        lock.release()


def confirm_mailing(chat_id: int):
    markup_object = types.InlineKeyboardMarkup()
    button_confirm = types.InlineKeyboardButton(
        text="✅ Отправить", callback_data="confirm_mailing"
    )
    button_cancel = types.InlineKeyboardButton(
        text="❌ Отмена", callback_data="cancel_mailing"
    )
    markup_object.add(button_confirm, button_cancel)

    get_and_send_message_without_duplicates(
        chat_id=chat_id,
        send_text="🚀 Вы действительно хотите выполнить рассылку?",
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

        if call.data == "cancel_mailing":
            db.remove_content()
            bot.send_message(chat_id=call.message.id, text="❌ Вы отменили рассылку.")
    except Exception as error:
        print("error", error)


if __name__ == "__main__":
    try:
        bot.infinity_polling(restart_on_change=True)
    except Exception as error:
        print("error by start server:", error)
