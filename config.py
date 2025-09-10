from telebot import types
from enum import Enum
from dotenv import load_dotenv

import os

load_dotenv(".env")

ADMIN_ID = os.getenv("ADMIN_ID", None)
FORMATTED_ADMIN_IDS = ADMIN_ID.split(",") if ADMIN_ID else []


class CommandNames(Enum):
    start = "start"
    start_mailing = "start_mailing"
    number_subscribers = "number_subscribers"
    about = "about"
    stop = "stop"
    done = "done"


BOT_COMMANDS = {f"/{cmd.value}" for cmd in CommandNames}


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


class CallbackData(Enum):
    create_order = "create_order"
    about = "about"
    link_to_site = "link_to_site"


COUNTRIES = [
    "Турция",
    "Египет",
    "ОАЭ",
    "Тайланд",
    "Китай",
    "Вьетнам",
    "Шри-Ланка",
    "Россия",
    "Куба",
    "Мальдивы",
    "Cейшелы",
    "Абхазия",
]

COUNT_DAYS = range(1, 14)

PREFIX_COUNTRY = "country_"
PREFIX_DAYS = "days_"
PREFIX_CURRENT_STEP = "step_"


def create_countries_button_menu(step: int) -> types.InlineKeyboardMarkup:
    markup_object = types.InlineKeyboardMarkup()

    row = []

    for index, country in enumerate(COUNTRIES):
        button_country = types.InlineKeyboardButton(
            text=country,
            callback_data=f"{PREFIX_COUNTRY}{country}-{PREFIX_CURRENT_STEP}{step}",
        )
        row.append(button_country)
        if (index + 1) % 3 == 0:
            markup_object.add(*row)
            row = []
    markup_object.add(
        types.InlineKeyboardButton(
            text="Не определились❓",
            callback_data=f"{PREFIX_COUNTRY}Не определились-{PREFIX_CURRENT_STEP}{step}",
        )
    )

    return markup_object


def create_days_button_menu(step: int) -> types.InlineKeyboardMarkup:
    markup_object = types.InlineKeyboardMarkup()

    row = []

    for number in COUNT_DAYS:
        days = number + 2
        button_country = types.InlineKeyboardButton(
            text=days, callback_data=f"{PREFIX_DAYS}{days}-{PREFIX_CURRENT_STEP}{step}"
        )
        row.append(button_country)
        if number % 3 == 0:
            markup_object.add(*row)
            row = []

    return markup_object
