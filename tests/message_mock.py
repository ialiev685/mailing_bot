import pytest


@pytest.fixture
def message_type_text_json_data():
    return {
        "content_type": "text",
        "id": 1,
        "message_id": 1,
        "from_user": {
            "id": 1,
            "is_bot": False,
            "first_name": "Ivan",
            "username": "iIvanov",
            "last_name": None,
            "language_code": "ru",
        },
        "date": 1754415464,
        "chat": {
            "id": 1,
        },
        "text": "Привет",
        "json": {
            "message_id": 2000,
            "from": {
                "id": 1,
                "is_bot": False,
                "first_name": "Ivan",
                "last_name": None,
                "username": "iIvanov",
                "language_code": "ru",
            },
            "chat": {
                "id": 1,
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "username": "iIvanov",
                "type": "private",
            },
            "date": 1754415464,
            "text": "Привет",
        },
    }


@pytest.fixture
def message_type_photo_json_data():
    return {
        "content_type": "photo",
        "id": 1,
        "message_id": 1,
        "from_user": {
            "id": 1,
            "is_bot": False,
            "first_name": "Ivan",
            "username": "iivanov",
            "last_name": None,
            "language_code": "ru",
        },
        "date": 1754415464,
        "chat": {
            "id": 1,
        },
        "text": "Привет",
        # если группв
        "media_group_id": "14035329655475426",
        "json": {
            "message_id": 2000,
            "from": {
                "id": 1,
                "is_bot": False,
                "first_name": "Ivan",
                "last_name": None,
                "username": "iivanov",
                "language_code": "ru",
            },
            "chat": {
                "id": 1,
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "username": "iivanov",
                "type": "private",
            },
            "date": 1754415464,
            "text": "Привет",
        },
        "photo": [
            {
                "file_id": "AgACAgIAAxkBAAIH0miSQeYr9UHFb8v3CQ_yH5M3_IegAALJ8zEb1ouRSOkgXw1dqrRvAQADAgADcwADNgQ",
                "file_unique_id": "AQADyfMxG9aLkUh4",
                "file_size": 1457,
                "width": 67,
                "height": 90,
            },
            {
                "file_id": "AgACAgIAAxkBAAIH0miSQeYr9UHFb8v3CQ_yH5M3_IegAALJ8zEb1ouRSOkgXw1dqrRvAQADAgADbQADNgQ",
                "file_unique_id": "AQADyfMxG9aLkUhy",
                "file_size": 31362,
                "width": 240,
                "height": 320,
            },
            {
                "file_id": "AgACAgIAAxkBAAIH0miSQeYr9UHFb8v3CQ_yH5M3_IegAALJ8zEb1ouRSOkgXw1dqrRvAQADAgADeAADNgQ",
                "file_unique_id": "AQADyfMxG9aLkUh9",
                "file_size": 177417,
                "width": 600,
                "height": 800,
            },
            {
                "file_id": "AgACAgIAAxkBAAIH0miSQeYr9UHFb8v3CQ_yH5M3_IegAALJ8zEb1ouRSOkgXw1dqrRvAQADAgADeQADNgQ",
                "file_unique_id": "AQADyfMxG9aLkUh-",
                "file_size": 356059,
                "width": 960,
                "height": 1280,
            },
        ],
    }


@pytest.fixture
def message_type_video_json_data():
    return {
        "content_type": "photo",
        "id": 1,
        "message_id": 1,
        "from_user": {
            "id": 1,
            "is_bot": False,
            "first_name": "Ivan",
            "username": "iIvanov",
            "last_name": None,
            "language_code": "ru",
        },
        "date": 1754415464,
        "chat": {
            "id": 1,
        },
        "text": "Привет",
        # если группв
        "media_group_id": "14035329655475426",
        "json": {
            "message_id": 2000,
            "from": {
                "id": 1,
                "is_bot": False,
                "first_name": "Ivan",
                "last_name": None,
                "username": "iivanov",
                "language_code": "ru",
            },
            "chat": {
                "id": 1,
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "username": "iivanov",
                "type": "private",
            },
            "date": 1754415464,
            "text": "Привет",
        },
        "video": {
            "file_id": "BAACAgIAAxkBAAIH2GiSRXAdcONM5g3dNK7k4KANXjrUAAL3ggAC1ouRSBPmrXgiIGpaNgQ",
            "file_unique_id": "AgAD94IAAtaLkUg",
            "width": 720,
            "height": 1280,
            "duration": 18,
            "file_name": "None",
            "mime_type": "video/mp4",
            "file_size": 23996773,
            "cover": "None",
            "start_timestamp": "None",
        },
    }
