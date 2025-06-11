from telebot import types


COMPLETE_EDIT_CONFIRM = "/done"


ADMIN_COMMANDS = [
    types.BotCommand("start", "Запуск бота"),
    types.BotCommand("start_mailing", "Начать рассылку"),
    types.BotCommand("number_subscribers", "Число подписчиков"),
]


USER_COMMANDS = [
    types.BotCommand("about", "О нас"),
    types.BotCommand("unsubscribe", "Отписаться"),
]
