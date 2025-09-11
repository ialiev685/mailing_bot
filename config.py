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
    "Не определились",
]

MONTHS = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]

SOCIAL_NETWORKS = [
    "По телефону",
    "whatsapp",
    "Telegram",
]


PRICES = [
    "до 100 000 ₽",
    "от 100 000 до 200 000 ₽",
    "от 200 000 до 300 000 ₽",
    "более 300 000 ₽",
]

COUNT_DAYS = range(1, 14)
COUNT_PEOPLE = [1, 2, 3, 4, 0]

PREFIX_CURRENT_STEP = "step_"
PREFIX_COUNTRY = "country_"
PREFIX_DAYS = "days_"
PREFIX_COUNT_PEOPLE = "people_"
PREFIX_MONTH = "month_"
PREFIX_PRICE = "price_"
PREFIX_SOCIAL = "SOCIAL_"


def create_countries_button_menu(step: int) -> types.InlineKeyboardMarkup:
    markup_object = types.InlineKeyboardMarkup()

    row = []

    for index, country in enumerate(COUNTRIES):
        button_country = types.InlineKeyboardButton(
            text=country,
            callback_data=f"{PREFIX_COUNTRY}{country}-{PREFIX_CURRENT_STEP}{step}",
        )
        row.append(button_country)
        if (index + 1) % 2 == 0:
            markup_object.add(*row)
            row = []
    if len(row) > 0:
        markup_object.add(*row)

    return markup_object


def create_days_button_menu(step: int) -> types.InlineKeyboardMarkup:
    markup_object = types.InlineKeyboardMarkup()

    row = []

    for number in COUNT_DAYS:
        days = number + 2
        button_days = types.InlineKeyboardButton(
            text=days, callback_data=f"{PREFIX_DAYS}{days}-{PREFIX_CURRENT_STEP}{step}"
        )
        row.append(button_days)
        if number % 3 == 0:
            markup_object.add(*row)
            row = []

    return markup_object


def create_count_people_button_menu(step: int) -> types.InlineKeyboardMarkup:
    markup_object = types.InlineKeyboardMarkup()

    row = []

    for number in COUNT_PEOPLE:
        button_count_people = types.InlineKeyboardButton(
            text="Другой вариант" if number == 0 else number,
            callback_data=f"{PREFIX_COUNT_PEOPLE}{number}-{PREFIX_CURRENT_STEP}{step}",
        )
        row.append(button_count_people)

        if number % 2 == 0:
            markup_object.add(*row)
            row = []
    if len(row) > 0:
        markup_object.add(*row)

    return markup_object


def create_month_button_menu(step: int) -> types.InlineKeyboardMarkup:
    markup_object = types.InlineKeyboardMarkup()

    row = []

    for index, month in enumerate(MONTHS):
        button_month = types.InlineKeyboardButton(
            text=month,
            callback_data=f"{PREFIX_MONTH}{month}-{PREFIX_CURRENT_STEP}{step}",
        )
        row.append(button_month)
        if (index + 1) % 3 == 0:
            markup_object.add(*row)
            row = []
    if len(row) > 0:
        markup_object.add(*row)

    return markup_object


def create_price_button_menu(step: int) -> types.InlineKeyboardMarkup:
    markup_object = types.InlineKeyboardMarkup()

    for price in PRICES:
        button_price = types.InlineKeyboardButton(
            text=price,
            callback_data=f"{PREFIX_PRICE}{price}-{PREFIX_CURRENT_STEP}{step}",
        )
        markup_object.add(button_price)

    return markup_object


def create_social_network_button_menu(step: int) -> types.InlineKeyboardMarkup:
    markup_object = types.InlineKeyboardMarkup()
    for month in SOCIAL_NETWORKS:
        button_social = types.InlineKeyboardButton(
            text=month,
            callback_data=f"{PREFIX_PRICE}{month}-{PREFIX_CURRENT_STEP}{step}",
        )
        markup_object.add(button_social)

    return markup_object
