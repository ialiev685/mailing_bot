from bot_core import bot
from config import CommandNames, is_admin
from helpers import handler_error_decorator
from telebot import types


@bot.message_handler(
    commands=[CommandNames.admin.value],
    func=lambda message: is_admin(message.from_user.id),
)
@handler_error_decorator(func_name="handle_call_admin_panel")
def handle_call_admin_panel(message: types.Message):

    markup_object = types.InlineKeyboardMarkup()
    button_start_mailing = types.InlineKeyboardButton(
        text="📨 Начать рассылку", callback_data=CommandNames.start_mailing.value
    )
    button_count_subscribes = types.InlineKeyboardButton(
        text="🧑‍🤝‍🧑 Количество подписчиков",
        callback_data=CommandNames.number_subscribers.value,
    )

    markup_object.add(button_start_mailing)
    markup_object.add(button_count_subscribes)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Выбирите необходимое действие, {message.from_user.first_name}\n",
        parse_mode="Markdown",
        reply_markup=markup_object,
    )
