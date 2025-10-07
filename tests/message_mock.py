import pytest
from telebot import types
from typing import Literal


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


class Video(types.Video):
    def __init__(self, file_id: str | None):
        super().__init__(
            file_id=file_id,
            file_unique_id="AgAD94IAAtaLkUg",
            width=720,
            height=1200,
            duration=18,
        )


class Chat(types.Chat):
    def __init__(self, chat_id=1):
        super().__init__(id=chat_id, type="private", first_name="ivanov")


class User(types.User):
    def __init__(self, user_id=1):
        super().__init__(
            id=user_id, first_name="ivanov", username="iivanov", is_bot=False
        )


class Message(types.Message):
    def __init__(
        self,
        content_type: Literal["text", "photo", "video"],
        user_id: int | None = None,
        chat_id: int | None = None,
        text: str = "",
        photo_variant_ids: list[str] | None = None,
        media_group_id: str | None = None,
        caption: str | None = None,
        video_file_id: str | None = None,
    ):
        super().__init__(
            message_id=1,
            from_user=User(user_id=user_id),
            date=1754843831,
            chat=Chat(chat_id=chat_id),
            content_type=content_type,
            json_string={},
            options={},
        )
        self.text = text
        self.photo: list[types.PhotoSize] = generate_photo(photo_variant_ids)
        self.media_group_id: str | None = media_group_id
        self.caption: str | None = caption
        self.video = Video(file_id=video_file_id)
