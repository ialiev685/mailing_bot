from telebot import types
from enum import Enum
from dotenv import load_dotenv
from typing import Callable, TypedDict
from enum import Enum
import os


STAND = os.getenv("STAND", "DEV").upper()


def init_env_file():
    if STAND == "DEV":
        load_dotenv(".env.dev")
    else:
        load_dotenv(".env.prod")


init_env_file()


ADMIN_ID = os.getenv("ADMIN_ID", None)
BOT_NAME = os.getenv("BOT_NAME", None)
CHAT_ID_SUPPORT = os.getenv("CHAT_ID_SUPPORT", None)
FORMATTED_ADMIN_IDS = ADMIN_ID.split(",") if ADMIN_ID else []
API_TOKEN = os.getenv("BOT_TOKEN", None)

CHAT_ID_FOR_SEND_ORDER = os.getenv("CHAT_ID_FOR_SEND_ORDER", None)
BOT_SENDER_ORDER_TOKEN = os.getenv("BOT_SENDER_ORDER_TOKEN")


def get_greeting(first_name: str) -> str:
    return f"Добрый день 👋, {first_name}. \n\nМеня зовут {BOT_NAME}. Я являюсь менеджером турагенства 'Ол Инклюзив' и помогу Вам организовать ваш лучший отдых. \n\n Выберите подходящий пункт меню чтобы подобрать тур"


class CommandNames(Enum):
    start = "start"
    about = "about"
    stop = "stop"
    done = "done"
    admin = "admin"
    order = "order"
    self_tour = "self_tour"


BOT_COMMANDS = {f"/{cmd.value}" for cmd in CommandNames}


USER_COMMANDS = [
    types.BotCommand(CommandNames.order.value, "Подобрать тур"),
    types.BotCommand(CommandNames.self_tour.value, "Свой тур"),
    types.BotCommand(CommandNames.about.value, "О нас"),
    types.BotCommand(CommandNames.stop.value, "Отписаться"),
]


def is_admin(user_id: int):
    if str(user_id) in FORMATTED_ADMIN_IDS:
        return True
    return False


class UsersCallbackData(Enum):
    create_order = "create_order"
    about = "about"
    link_to_site = "link_to_site"


class AdminCallbackData(Enum):
    start_mailing = "start_mailing"
    number_subscribers = "number_subscribers"
    upload_about_us = "upload_about_us"


class Step(Enum):
    step_1 = 1
    step_2 = 2
    step_3 = 3
    step_4 = 4
    step_5 = 5
    step_6 = 6


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
    "В whatsapp",
    "В telegram",
]


PRICES = [
    "до 100 000 ₽",
    "от 100 000 до 200 000 ₽",
    "от 200 000 до 300 000 ₽",
    "более 300 000 ₽",
]

COUNT_DAYS = [str(day) for day in range(3, 15)]
COUNT_PEOPLE = ["1", "2", "3", "4", "Другой вариант"]

PREFIX_CURRENT_STEP = "step_"
PREFIX_COUNTRY = "country_"
PREFIX_DAYS = "days_"
PREFIX_COUNT_PEOPLE = "people_"
PREFIX_MONTH = "month_"
PREFIX_PRICE = "price_"
PREFIX_SOCIAL = "social_"
PREFIX_CONFIRM_EDIT_ABOUT_US_CONTENT = "confirm_edit_about_us_content_"
PREFIX_CANCEL_EDIT_ABOUT_US_CONTENT = "cancel_edit_about_us_content_"


def create_callback_data_for_button(step: int, prefix_name: str, value: str):
    return f"{prefix_name}{value}-{PREFIX_CURRENT_STEP}{step}"


def factory_menu(
    step: int, menu_names: list[str], prefix_name: str, count_column: int = 0
) -> types.InlineKeyboardMarkup:
    markup_object = types.InlineKeyboardMarkup()

    row = []

    for index, value in enumerate(menu_names):
        button = types.InlineKeyboardButton(
            text=value,
            callback_data=create_callback_data_for_button(
                step=step, prefix_name=prefix_name, value=value
            ),
        )
        if count_column == 0:
            markup_object.add(button)
            continue

        row.append(button)

        if (index + 1) % count_column == 0:
            markup_object.add(*row)
            row = []

    if count_column > 0 and len(row) > 0:
        markup_object.add(*row)

    return markup_object


def create_countries_button_menu(step: int) -> types.InlineKeyboardMarkup:
    return factory_menu(
        step=step, menu_names=COUNTRIES, prefix_name=PREFIX_COUNTRY, count_column=2
    )


def create_days_button_menu(step: int) -> types.InlineKeyboardMarkup:
    return factory_menu(
        step=step, menu_names=COUNT_DAYS, prefix_name=PREFIX_DAYS, count_column=3
    )


def create_count_people_button_menu(step: int) -> types.InlineKeyboardMarkup:
    return factory_menu(
        step=step,
        menu_names=COUNT_PEOPLE,
        prefix_name=PREFIX_COUNT_PEOPLE,
        count_column=2,
    )


def create_month_button_menu(step: int) -> types.InlineKeyboardMarkup:
    return factory_menu(
        step=step, menu_names=MONTHS, prefix_name=PREFIX_MONTH, count_column=3
    )


def create_price_button_menu(step: int) -> types.InlineKeyboardMarkup:
    return factory_menu(step=step, menu_names=PRICES, prefix_name=PREFIX_PRICE)


def create_social_network_button_menu(step: int) -> types.InlineKeyboardMarkup:
    return factory_menu(
        step=step, menu_names=SOCIAL_NETWORKS, prefix_name=PREFIX_SOCIAL
    )


class StepOptions(TypedDict):
    get_menu: Callable[[int], types.InlineKeyboardMarkup]
    title: str


STEP_OPTIONS: dict[int, StepOptions] = {
    Step.step_1.value: {
        "title": "Выберите направление для отдыха:",
        "get_menu": create_countries_button_menu,
    },
    Step.step_2.value: {
        "title": "На сколько дней планируете Ваш отдых?",
        "get_menu": create_days_button_menu,
    },
    Step.step_3.value: {
        "title": "Сколько человек отправится?",
        "get_menu": create_count_people_button_menu,
    },
    Step.step_4.value: {
        "title": "Выберите месяц для отпуска:",
        "get_menu": create_month_button_menu,
    },
    Step.step_5.value: {
        "title": "Выберите примерные бюджет:",
        "get_menu": create_price_button_menu,
    },
    Step.step_6.value: {
        "title": "Выберите как с вами связаться:",
        "get_menu": create_social_network_button_menu,
    },
}
