from bot_core import bot
from .order import set_number_phone_after_create_order, is_response_to_phone_message
from .mailing import handle_text_messages, is_access_to_mailing
from telebot import types
from config import BOT_COMMANDS


@bot.message_handler(
    content_types=["text"],
    func=lambda message: not message.text in BOT_COMMANDS
    and (
        is_response_to_phone_message(message=message)
        or is_access_to_mailing(user_id=message.from_user.id)
    ),
)
def route_by_text_type(message: types.Message):
    if is_response_to_phone_message(message=message):
        set_number_phone_after_create_order(message=message)
    elif message.from_user and (
        is_access_to_mailing(user_id=message.from_user.id)
        and message.reply_to_message is None
    ):
        handle_text_messages(message=message)
