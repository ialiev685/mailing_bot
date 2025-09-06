from bot_core import bot
from config import CallbackData, create_countries_button_menu
from telebot import types


@bot.callback_query_handler(
    func=lambda call: call.data in [CallbackData.create_order.value]
)
def create_order(call: types.CallbackQuery):

    button_menu = create_countries_button_menu()

    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"*Шаг 1 из 2*\n\n Выберите направление:",
        parse_mode="Markdown",
        reply_markup=button_menu,
    )
