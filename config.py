from telebot import types
from enum import Enum


class CommandNames(Enum):
    start = "start"
    start_mailing = "start_mailing"
    number_subscribers = "number_subscribers"
    about = "about"
    stop = "stop"
    done = "done"


ADMIN_COMMANDS = [
    types.BotCommand(CommandNames.start.value, "Запуск бота"),
    types.BotCommand(CommandNames.start_mailing.value, "Начать рассылку"),
    types.BotCommand(CommandNames.number_subscribers.value, "Число подписчиков"),
    types.BotCommand(CommandNames.stop.value, "Отписаться"),
]


USER_COMMANDS = [
    types.BotCommand(CommandNames.about.value, "О нас"),
    types.BotCommand(CommandNames.stop.value, "Отписаться"),
]


PATH_MAILING_DATA = "mailing_data/data.json"
