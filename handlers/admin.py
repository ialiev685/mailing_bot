from typing import Literal
from bot_core import bot
from config import (
    CommandNames,
    AdminCallbackData,
    is_admin,
    PREFIX_CONFIRM_EDIT_ABOUT_US_CONTENT,
    PREFIX_CANCEL_EDIT_ABOUT_US_CONTENT,
)
from helpers import get_optimal_photo, handler_error_decorator, has_value_in_data_name
from telebot import types
import database.controllers as db
import re


CONTENT_ABOUT_US = "📥 Загрузите фотографию с описанием."


def get_ids_from_callback_data(
    data: str,
) -> dict[Literal["message_id", "chat_id"], int] | None:
    response = re.search(
        r"{}(\d+)-(\d+)".format(PREFIX_CONFIRM_EDIT_ABOUT_US_CONTENT), data
    )
    if response:
        message_id = int(response.group(1))
        chat_id = int(response.group(2))
        return {"message_id": message_id, "chat_id": chat_id}
    return None


@bot.callback_query_handler(
    func=lambda call: call.data == AdminCallbackData.number_subscribers.value
    and is_admin(user_id=call.from_user.id),
)
@handler_error_decorator(func_name="handle_number_subscribers")
def get_number_subscribers(call: types.CallbackQuery):
    bot.answer_callback_query(callback_query_id=call.id)

    count = db.get_count_users()
    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Количество подписчиков - *{count}*",
        parse_mode="Markdown",
    )


@bot.callback_query_handler(
    func=lambda call: call.data == AdminCallbackData.upload_about_us.value
    and is_admin(user_id=call.from_user.id),
)
@handler_error_decorator(func_name="handle_set_content_about_us")
def set_content_about_us(call: types.CallbackQuery):
    bot.answer_callback_query(callback_query_id=call.id)
    msg = bot.send_message(chat_id=call.message.chat.id, text=CONTENT_ABOUT_US)
    bot.register_next_step_handler(message=msg, callback=upload_content_about_us)


@handler_error_decorator(func_name="handle_upload_content_about_us")
def upload_content_about_us(message: types.Message):
    if (
        message.content_type == "photo"
        and message.from_user
        and is_admin(message.from_user.id)
    ):

        if message.media_group_id is not None:
            bot.reply_to(message=message, text="⚠️ Загрузите только одноу фотографию.")
            return
        if message.caption is None:
            bot.reply_to(message=message, text="⚠️ Добавьте описание к фтографии.")
            return

        photo = get_optimal_photo(photo_list=message.photo)
        db.create_about_us_data(
            message_id=message.message_id,
            chat_id=message.chat.id,
            file_id=photo.file_id,
            caption=message.caption,
        )

        markup_object = types.InlineKeyboardMarkup()
        button_confirm = types.InlineKeyboardButton(
            text="✅ Принять",
            callback_data=f"{PREFIX_CONFIRM_EDIT_ABOUT_US_CONTENT}{message.message_id}-{message.chat.id}",
        )
        button_cancel = types.InlineKeyboardButton(
            text="❌ Отменить",
            callback_data=f"{PREFIX_CANCEL_EDIT_ABOUT_US_CONTENT}{message.message_id}-{message.chat.id}",
        )
        markup_object.add(button_confirm, button_cancel)

        bot.send_message(
            chat_id=message.chat.id,
            text="🔧 Вы действительно хотите изменить контент?",
            reply_markup=markup_object,
            parse_mode="Markdown",
        )


@bot.callback_query_handler(
    func=lambda call: (
        has_value_in_data_name(PREFIX_CONFIRM_EDIT_ABOUT_US_CONTENT)(call)
        or has_value_in_data_name(PREFIX_CANCEL_EDIT_ABOUT_US_CONTENT)(call)
    )
    and is_admin(user_id=call.from_user.id),
)
@handler_error_decorator(func_name="handle_number_subscribers")
def confirm_upload_about_us_content(call: types.CallbackQuery):
    bot.answer_callback_query(callback_query_id=call.id)

    if call.data:

        parsed_ids = get_ids_from_callback_data(call.data)

        if not parsed_ids:
            return
        bot.delete_message(
            chat_id=call.message.chat.id, message_id=call.message.message_id
        )
        if call.data.startswith(PREFIX_CONFIRM_EDIT_ABOUT_US_CONTENT):

            updated_content = db.update_about_us_data(
                chat_id=parsed_ids["chat_id"], message_id=parsed_ids["message_id"]
            )
            if updated_content:
                db.remove_about_us_data(chat_id=parsed_ids["chat_id"])
                bot.send_message(
                    chat_id=parsed_ids["chat_id"],
                    text="✅ Контент обновлен.",
                    parse_mode="Markdown",
                )

        elif call.data.startswith(PREFIX_CANCEL_EDIT_ABOUT_US_CONTENT):
            db.remove_about_us_data(chat_id=parsed_ids["chat_id"])


# Меню


@bot.message_handler(
    commands=[CommandNames.admin.value],
    func=lambda message: is_admin(message.from_user.id),
)
@handler_error_decorator(func_name="handle_call_admin_panel")
def handle_call_admin_panel(message: types.Message):

    markup_object = types.InlineKeyboardMarkup()
    button_start_mailing = types.InlineKeyboardButton(
        text="📨 Начать рассылку", callback_data=AdminCallbackData.start_mailing.value
    )
    button_count_subscribes = types.InlineKeyboardButton(
        text="🧑‍🤝‍🧑 Количество подписчиков",
        callback_data=AdminCallbackData.number_subscribers.value,
    )
    button_upload_about_us_content = types.InlineKeyboardButton(
        text="🎬 Загрузить контент о себе",
        callback_data=AdminCallbackData.upload_about_us.value,
    )

    markup_object.add(button_start_mailing)
    markup_object.add(button_count_subscribes)
    markup_object.add(button_upload_about_us_content)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Выбирите необходимое действие\n",
        parse_mode="Markdown",
        reply_markup=markup_object,
    )
