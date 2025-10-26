from typing import Union
from telebot import types
from config import (
    CommandNames,
    BOT_COMMANDS,
    is_admin,
    AdminCallbackData,
)
from object_types import (
    MailingContentType,
    MailingTextContentTypeModel,
    MailingPhotoContentTypeModel,
    MailingContentGroupDict,
)


from time import sleep
from helpers import (
    create_button_with_url_or_data_and_separate_content,
    get_formatted_content,
    create_media_group,
)
from helpers import handler_error_decorator
from database.models import SubscriberModel
import database.controllers as db
from bot_core import bot


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
        set_value_about_start_mailing(value=False)


def is_access_to_mailing(user_id: int, text: str | None = None) -> bool:
    start_mailing_data = db.get_start_mailing_data()
    if text and text in BOT_COMMANDS:
        return False
    if not is_admin(user_id=user_id) or start_mailing_data.value is not True:
        return False
    return True


@bot.message_handler(commands=[CommandNames.stop.value])
@handler_error_decorator(func_name="handle_unsubscribe")
def handle_unsubscribe(message: types.Message):
    if message.from_user:
        db.unsubscribe_user(message.from_user.id)
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Вы отписались 😢",
            parse_mode="Markdown",
        )


@bot.callback_query_handler(
    func=lambda call: call.data == AdminCallbackData.start_mailing.value
    and is_admin(user_id=call.from_user.id),
)
@handler_error_decorator(
    callBack=send_message_about_mailing_error,
    func_name="handle_control_start_mailing",
)
def handle_control_start_mailing(call: types.CallbackQuery):
    bot.answer_callback_query(callback_query_id=call.id)
    set_value_about_start_mailing(value=True)
    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"✍️ Вставьте сообщение (фото или текст, можно несколько) для рассылки.\n\n*Выполните команду /{CommandNames.done.value} когда закончите вставку необходимого контента.*",
        parse_mode="Markdown",
    )


@bot.message_handler(
    commands=[CommandNames.done.value],
    func=lambda message: is_access_to_mailing(user_id=message.from_user.id),
)
@handler_error_decorator(
    callBack=send_message_about_mailing_error,
    func_name="handle_control_done_add_content",
)
def handle_control_done_add_content(message: types.Message):
    if message.text == f"/{CommandNames.done.value}":
        if db.check_content() == False:
            bot.send_message(
                chat_id=message.chat.id,
                text=f"❌ У вас нет сообщений для рассылки.",
                parse_mode="Markdown",
            )
            return

        confirm_mailing(chat_id=message.chat.id)


@handler_error_decorator(
    callBack=send_message_about_mailing_error, func_name="handle_text_messages"
)
def handle_text_messages(message: types.Message):
    content = get_formatted_content(message)
    if content is not None:
        db.add_mailing_content(content)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"✅ Сообщение добавлено. *Отправьте еще или нажмите /{CommandNames.done.value} для завершения.*",
        parse_mode="Markdown",
    )


@bot.message_handler(
    content_types=["photo", "video"],
    func=lambda message: is_access_to_mailing(
        user_id=message.from_user.id, text=message.text
    ),
)
@handler_error_decorator(
    callBack=send_message_about_mailing_error, func_name="handle_media_messages"
)
def handle_media_messages(message: types.Message):
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
        text="👀 Предосмотр", callback_data="preview_content"
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


def send_content_to_chat_by_id(
    content_group: dict[str, Union[MailingContentType, list[MailingContentType]]],
    chat_id: int,
):
    for key, content in content_group.items():
        if isinstance(content, MailingTextContentTypeModel):

            formatted_text = content.text if content.text else ""
            result = create_button_with_url_or_data_and_separate_content(formatted_text)
            bot.send_message(
                chat_id=chat_id,
                text=result["cleared_text"],
                parse_mode="Markdown",
                reply_markup=result["button_object"],
            )
        elif isinstance(content, MailingPhotoContentTypeModel):
            formatted_caption = content.caption if content.caption else ""
            result = create_button_with_url_or_data_and_separate_content(
                formatted_caption
            )
            bot.send_photo(
                chat_id=chat_id,
                caption=result["cleared_text"],
                photo=content.file_id,
                parse_mode="Markdown",
                reply_markup=result["button_object"],
            )

        elif isinstance(content, list):
            media = create_media_group(content_list=content)
            bot.send_media_group(chat_id=chat_id, media=media)
        sleep(0.3)


@bot.callback_query_handler(
    func=lambda call: (
        call.data in ["confirm_mailing", "cancel_mailing", "preview_content"]
    )
    and is_access_to_mailing(call.from_user.id)
)
@handler_error_decorator(
    callBack=send_message_about_mailing_error, func_name="handle_confirm_mailing"
)
def handle_confirm_mailing(call: types.CallbackQuery):
    bot.answer_callback_query(callback_query_id=call.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    if call.data == "preview_content":
        sorted_group_content_preview: MailingContentGroupDict = db.get_mailing_content()
        send_content_to_chat_by_id(
            content_group=sorted_group_content_preview, chat_id=call.message.chat.id
        )
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"👆 *Это предосмотр контента перед рассылкой*\n",
            parse_mode="Markdown",
        )
        confirm_mailing(chat_id=call.message.chat.id)
        return

    if call.data == "confirm_mailing":
        users: list[SubscriberModel] = db.get_users()
        sorted_group_content: MailingContentGroupDict = db.get_mailing_content()

        for user in users:
            send_content_to_chat_by_id(
                content_group=sorted_group_content, chat_id=user.chat_id
            )

        set_value_about_start_mailing(value=False)

    if call.data == "cancel_mailing":
        set_value_about_start_mailing(value=False)
        bot.send_message(
            chat_id=call.message.chat.id,
            text="❌ Вы отменили рассылку.",
            parse_mode="Markdown",
        )
