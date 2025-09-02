from telebot import types
from enum import Enum
from dotenv import load_dotenv

import os

load_dotenv(".env")

ADMIN_ID = os.getenv("ADMIN_ID", None)
FORMATTED_ADMIN_IDS = ADMIN_ID.split(",") if ADMIN_ID else []


class CommandNames(Enum):
    start = "start"
    preview = "preview"
    start_mailing = "start_mailing"
    number_subscribers = "number_subscribers"
    about = "about"
    stop = "stop"
    done = "done"


BOT_COMMANDS = {f"/{cmd.value}" for cmd in CommandNames}


ADMIN_COMMANDS = [
    # types.BotCommand(CommandNames.start.value, "Запуск бота"),
    types.BotCommand(CommandNames.start_mailing.value, "Начать рассылку"),
    types.BotCommand(CommandNames.start_mailing.preview, "Предосмотр рассылки"),
    types.BotCommand(CommandNames.number_subscribers.value, "Число подписчиков"),
    types.BotCommand(CommandNames.stop.value, "Отписаться"),
]


USER_COMMANDS = [
    types.BotCommand(CommandNames.about.value, "О нас"),
    types.BotCommand(CommandNames.stop.value, "Отписаться"),
]


PATH_MAILING_DATA = "mailing_data/data.json"
