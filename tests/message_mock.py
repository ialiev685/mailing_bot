import pytest
from telebot import types
from typing import Literal


photos_mock = [
    types.PhotoSize(
        file_id="AgACAgIAAxkBAAIH0miSQeYr9UHFb8v3CQ_yH5M3_IegAALJ8zEb1ouRSOkgXw1dqrRvAQADAgADcwADNgQ",
        file_unique_id="AQADzqoxGx4C6M0B",
        width=160,
        height=160,
    ),
    types.PhotoSize(
        file_id="AgACAgIAAxkBAAIH0miSQeYr9UHFb8v3CQ_yH5M3_IegAALJ8zEb1ouRSOkgXw1dqrRvAQADAgADbQADNgQ",
        file_unique_id="AQADzqoxGx4C6M0B",
        width=320,
        height=320,
    ),
    types.PhotoSize(
        file_id="AgACAgIAAxkBAAIH0miSQeYr9UHFb8v3CQ_yH5M3_IegAALJ8zEb1ouRSOkgXw1dqrRvAQADAgADeAADNgQ",
        file_unique_id="AQADzqoxGx4C6M0B",
        width=480,
        height=480,
    ),
    types.PhotoSize(
        file_id="AgACAgIAAxkBAAIH0miSQeYr9UHFb8v3CQ_yH5M3_IegAALJ8zEb1ouRSOkgXw1dqrRvAQADAgADeQADNgQ",
        file_unique_id="AQADzqoxGx4C6M0B",
        width=640,
        height=640,
    ),
]


video_mock = (
    {
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
)


def generate_photo(photo_ids: list[str] | None) -> list[types.PhotoSize]:
    photo_data = []

    if photo_ids:
        for id in photo_ids:
            photo_data.append(
                types.PhotoSize(
                    file_id=id,
                    file_unique_id=id,
                    width=160,
                    height=160,
                ),
            )

    return photo_data


class Chat(types.Chat):
    def __init__(self):
        super().__init__(id=1, type="private", first_name="ivanov")


class User(types.User):
    def __init__(self):
        super().__init__(id=1, first_name="ivanov", username="iivanov", is_bot=False)


class Message(types.Message):
    def __init__(
        self,
        content_type: Literal["text", "photo", "video"],
        text: str = "",
        photo_variant_ids: list[str] | None = None,
        media_group_id: str | None = None,
        caption: str | None = None,
    ):
        super().__init__(
            message_id=1,
            from_user=User(),
            date=1754843831,
            chat=Chat(),
            content_type=content_type,
            json_string={},
            options={},
        )
        self.text = text
        self.photo: list[types.PhotoSize] = generate_photo(photo_variant_ids)
        self.media_group_id: str | None = media_group_id
        self.caption: str | None = caption
