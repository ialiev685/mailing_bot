import telebot
from telebot import types
from config import (
    ADMIN_COMMANDS,
    FORMATTED_ADMIN_IDS,
    USER_COMMANDS,
    CommandNames,
    BOT_COMMANDS,
)
from object_types import (
    RoleEnum,
    MailingContentType,
    MailingTextContentTypeModel,
    MailingPhotoContentTypeModel,
)
from collections import defaultdict
from dotenv import load_dotenv
from time import sleep
from helpers import get_formatted_content, create_media_group
from helpers import handler_error_decorator
from database.models import SubscriberModel
import database.controllers as db
from threading import Lock
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv(".env")

API_TOKEN = os.getenv("BOT_TOKEN", None)
APP_PORT = os.getenv("APP_PORT", None)


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


def set_value_about_start_mailing(value: bool):
    db.update_flag_start_mailing(value=value)
    db.remove_content()


def send_message_about_mailing_error(*args):
    message: types.Message | None = None

    for arg in args:
        if hasattr(arg, "message") and hasattr(arg.message, "chat"):
            message = arg.message
            break

    if message:
        bot.send_message(
            chat_id=message.chat.id,
            text="⚠️ Произошла ошибка при обработке сообщения. Запустите рассылку заново или обратитесь к администратору.",
            parse_mode="Markdown",
        )
        db.update_flag_start_mailing(value=False)
        db.remove_content()


@bot.message_handler(commands=[CommandNames.start.value])
@handler_error_decorator(
    callBack=send_message_about_mailing_error, func_name="handle_subscribe"
)
def handle_subscribe(message: types.Message):

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

    if is_admin(message.from_user.id):

        set_menu_for_admin(chat_id=message.chat.id)

        db.init_flag_start_mailing()

    else:
        set_menu_for_user(chat_id=message.chat.id)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Привет 👋, {message.from_user.first_name} {message.from_user.last_name if message.from_user.last_name else '' }",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=[CommandNames.stop.value])
@handler_error_decorator(
    callBack=send_message_about_mailing_error, func_name="handle_unsubscribe"
)
def handle_unsubscribe(message: types.Message):

    db.unsubscribe_user(message.from_user.id)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Вы отписались 😢",
        parse_mode="Markdown",
    )


@handler_error_decorator(
    callBack=send_message_about_mailing_error, func_name="start_mailing"
)
def start_mailing(message: types.Message):

    set_value_about_start_mailing(value=True)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"✍️ Вставьте сообщение (фото или текст, можно несколько) для рассылки.\n\n*Выполните команду /{CommandNames.done.value} когда закончите вставку необходимого контента.*",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=[CommandNames.number_subscribers.value])
@handler_error_decorator(
    callBack=send_message_about_mailing_error,
    func_name="handle_number_subscribers",
)
def handle_number_subscribers(message: types.Message):

    count = db.get_count_users()
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Количество подписчиков - *{count}*",
        parse_mode="Markdown",
    )


@bot.message_handler(
    commands=[CommandNames.done.value, CommandNames.start_mailing.value]
)
@handler_error_decorator(
    callBack=send_message_about_mailing_error,
    func_name="handle_control_start_mailing",
)
def handle_control_start_mailing(message: types.Message):

    if message.text == f"/{CommandNames.done.value}":
        if db.check_content() == False:
            bot.send_message(
                chat_id=message.chat.id,
                text=f"❌ У вас нет сообщений для рассылки.",
                parse_mode="Markdown",
            )
            return

        confirm_mailing(message.chat.id)
        return
    if message.text == f"/{CommandNames.start_mailing.value}":
        start_mailing(message=message)


@bot.message_handler(content_types=["text"])
@handler_error_decorator(
    callBack=send_message_about_mailing_error, func_name="handle_text_messages"
)
def handle_text_messages(message: types.Message):
    # Пропускаем команды, которые уже обработаны другим хэндлером
    if message.text in BOT_COMMANDS:
        return

    start_mailing_data = db.get_start_mailing_data()
    if start_mailing_data.value is not True:
        return

    content = get_formatted_content(message)

    if content is not None:
        db.add_mailing_content(content)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"✅ Сообщение добавлено. *Отправьте еще или нажмите /{CommandNames.done.value} для завершения.*",
        parse_mode="Markdown",
    )


@bot.message_handler(content_types=["photo", "video"])
@handler_error_decorator(
    callBack=send_message_about_mailing_error, func_name="handle_media_messages"
)
def handle_media_messages(message: types.Message):
    start_mailing_data = db.get_start_mailing_data()
    if start_mailing_data.value is not True:
        return

    content = get_formatted_content(message)

    # Для медиа используем задержку перед ответом
    sleep(0.3)

    if content is not None:
        db.add_mailing_content(content)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"✅ Сообщение добавлено. *Отправьте еще или нажмите /{CommandNames.done.value} для завершения.*",
        parse_mode="Markdown",
    )


@handler_error_decorator(
    callBack=send_message_about_mailing_error, func_name="confirm_mailing"
)
def confirm_mailing(chat_id: int):
    markup_object = types.InlineKeyboardMarkup()
    button_preview = types.InlineKeyboardButton(
        text="👀 Предосмотр", callback_data="preview"
    )
    button_confirm = types.InlineKeyboardButton(
        text="✅ Отправить", callback_data="confirm_mailing"
    )
    button_cancel = types.InlineKeyboardButton(
        text="❌ Отмена", callback_data="cancel_mailing"
    )
    markup_object.add(button_confirm, button_cancel)
    markup_object.add(button_preview)

    bot.send_message(
        chat_id=chat_id,
        text="🚀 Вы действительно хотите выполнить рассылку?",
        parse_mode="Markdown",
        reply_markup=markup_object,
    )


@bot.callback_query_handler(
    func=lambda call: call.data in ["confirm_mailing", "cancel_mailing"]
)
@handler_error_decorator(
    callBack=send_message_about_mailing_error, func_name="handle_confirm_mailing"
)
def handle_confirm_mailing(call: types.CallbackQuery):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    if call.data == "confirm_mailing":

        users: list[SubscriberModel] = db.get_users()

        sorted_group_content: defaultdict[str, list[MailingContentType]] = (
            db.get_mailing_content()
        )

        for user in users:

            for key, content in sorted_group_content.items():
                if len(content) < 1:
                    continue
                if isinstance(content, MailingTextContentTypeModel):
                    bot.send_message(
                        chat_id=user.chat_id,
                        text=content.text,
                        parse_mode="Markdown",
                    )
                elif isinstance(content, MailingPhotoContentTypeModel):
                    bot.send_photo(
                        chat_id=user.chat_id,
                        caption=content.caption,
                        photo=content.file_id,
                        parse_mode="Markdown",
                    )

                elif isinstance(content, list):
                    media = create_media_group(content_list=content)
                    bot.send_media_group(chat_id=user.chat_id, media=media)
                sleep(0.3)

        set_value_about_start_mailing(value=False)

    if call.data == "cancel_mailing":
        set_value_about_start_mailing(value=False)
        bot.send_message(chat_id=call.message.id, text="❌ Вы отменили рассылку.")


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
            # bot.infinity_polling(restart_on_change=True)
            bot.infinity_polling()

        except Exception as error:
            sleep(10)
            print("error by start server:", error)
