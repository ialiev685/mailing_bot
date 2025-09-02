from sqlalchemy.orm import Session
import database.controllers as db
from telebot import types
from tests.core_testing import *
from helpers import get_formatted_content, create_media_group
from tests.core_testing import *
from tests.message_mock import Message
from object_types import MailingPhotoContentTypeModel, MailingTextContentTypeModel

from typing import TypedDict, Literal, Optional


class TaskData(TypedDict, total=False):
    content_type: Literal["photo", "text", "video"]
    photo_variant_ids: Optional[list[str]]
    media_group_id: Optional[str]
    caption: Optional[str]
    text: Optional[str]
    video_file_id: Optional[str]


def add_content(test_list: list[TaskData], session: Session):

    for task in test_list:
        message_type_photo_has_group = Message(
            content_type=task["content_type"],
            photo_variant_ids=task.get("photo_variant_ids"),
            media_group_id=task.get("media_group_id"),
            text=task.get("text") or "",
            caption=task.get("caption"),
            video_file_id=task.get("video_file_id"),
        )

        formatted_content = get_formatted_content(message=message_type_photo_has_group)

        if formatted_content:
            db.add_mailing_content_impl(content_data=formatted_content, session=session)


class TestMailingContent:
    def test_add_mailing_content_text_and_photo_type(self, session_testing: Session):

        test_list: list[TaskData] = [
            {
                "content_type": "text",
                "text": "test description 1",
            },
            {
                "content_type": "photo",
                "photo_variant_ids": ["01", "02", "03", "04"],
            },
            {
                "content_type": "text",
                "text": "test description 2",
            },
            {
                "content_type": "photo",
                "photo_variant_ids": ["01"],
                "caption": "test photo",
            },
        ]

        add_content(test_list=test_list, session=session_testing)

        sorted_group_content = db.get_mailing_content_impl(session=session_testing)

        assert len(sorted_group_content) == 4

        for key, message in sorted_group_content.items():
            if isinstance(message, MailingTextContentTypeModel):
                assert (
                    message.text == "test description 1"
                    if key == "0"
                    else message.text == "test description 2"
                )
                assert message.media_group_id is None
                assert message.content_type == "text"
            elif isinstance(message, MailingPhotoContentTypeModel):
                assert message.media_group_id is None
                assert (
                    message.file_id == "03" if key == "1" else message.file_id == "01"
                )
                assert (
                    message.caption == "test photo"
                    if key == "3"
                    else message.caption is None
                )
                assert message.content_type == "photo"
            else:
                raise ValueError("тесты не прошли")

    def test_add_mailing_content_text_photo_video_type_with_group(
        self, session_testing: Session
    ):

        test_list: list[TaskData] = [
            {
                "content_type": "text",
                "text": "test description 1",
            },
            {
                "content_type": "photo",
                "media_group_id": "14035329655475426",
                "photo_variant_ids": ["01", "02", "03", "04"],
            },
            {
                "content_type": "text",
                "text": "test description 2",
            },
            {
                "content_type": "photo",
                "media_group_id": "14035329655475426",
                "photo_variant_ids": ["01", "02"],
                "caption": "test photo",
            },
            {
                "content_type": "video",
                "media_group_id": "14035329655475427",
                "caption": "test video",
                "video_file_id": "001",
            },
            {
                "content_type": "video",
                "media_group_id": "14035329655475427",
                "video_file_id": "002",
            },
        ]

        add_content(test_list=test_list, session=session_testing)

        sorted_group_content = db.get_mailing_content_impl(session=session_testing)

        assert len(sorted_group_content) == 4

        for index, item in enumerate(sorted_group_content.items()):
            key, content = item
            if index == 0:
                assert content.content_type == "text"
                assert content.text == f"test description 1"
                assert content.media_group_id is None

            elif index == 1:
                assert len(content) == 2
                assert key == "14035329655475426"
                assert isinstance(content, list)
                assert content[0].content_type == "photo"
                assert content[1].content_type == "photo"
                media = create_media_group(content_list=content)
                assert media[0].caption == "test photo"
                assert media[0].media == "03"
                assert media[1].caption is None
                assert media[1].media == "02"

            elif index == 2:
                assert content.content_type == "text"
                assert content.text == f"test description 2"
                assert content.media_group_id is None

            elif index == 3:
                assert len(content) == 2
                assert key == "14035329655475427"
                assert isinstance(content, list)
                assert content[0].content_type == "video"
                assert content[1].content_type == "video"
                media = create_media_group(content_list=content)
                assert media[0].caption == "test video"
                assert media[0].media == "001"
                assert media[1].caption is None
                assert media[1].media == "002"

            else:
                raise ValueError("тесты не прошли")
