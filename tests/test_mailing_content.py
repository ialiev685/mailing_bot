from sqlalchemy.orm import Session
import database.controllers as db
from telebot import types
from tests.message_mock import *
from tests.core_testing import *
from helpers import get_formatted_content, create_media_group
import database.controllers as db
from tests.core_testing import *
from tests.message_mock import Message
from object_types import (
    MailingPhotoContentTypeModel,
    MailingTextContentTypeModel,
    MailingVideoContentTypeModel,
    MailingContentType,
)

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

        sorted_single_content, sorted_group_content = db.get_mailing_content_impl(
            session=session_testing
        )

        assert len(sorted_single_content) == 4
        assert len(sorted_group_content) == 0

        for index, message in enumerate(sorted_single_content):
            if isinstance(message, MailingTextContentTypeModel):
                assert (
                    message.text == "test description 1"
                    if index == 0
                    else message.text == "test description 2"
                )
                assert message.media_group_id is None
                assert message.content_type == "text"
            elif isinstance(message, MailingPhotoContentTypeModel):
                assert message.media_group_id is None
                assert (
                    message.file_id == "03" if index == 1 else message.file_id == "01"
                )
                assert (
                    message.caption == "test photo"
                    if index == 3
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

        sorted_single_content, sorted_group_content = db.get_mailing_content_impl(
            session=session_testing
        )

        assert len(sorted_single_content) == 2
        assert len(sorted_group_content) == 2

        for index, message in enumerate(sorted_single_content):
            if isinstance(message, MailingTextContentTypeModel):
                assert message.content_type == "text"
                assert message.text == f"test description {index+1}"
                assert message.media_group_id is None

            else:
                raise ValueError("тесты не прошли")

        for key, contents in sorted_group_content.items():

            media = create_media_group(
                content_list=contents, input=types.InputMediaPhoto
            )
            if key == "14035329655475426":
                assert media[0].caption == "test photo"
            elif key == "14035329655475427":
                assert media[0].caption == "test video"

            assert len(contents) == 2

            for index, message in enumerate(contents):
                if isinstance(message, MailingPhotoContentTypeModel):
                    assert (
                        message.caption == "test photo"
                        if index == 1
                        else message.caption is None
                    )
                    assert message.media_group_id == "14035329655475426"
                    assert message.content_type == "photo"
                    assert (
                        message.file_id == "03"
                        if index == 0
                        else message.file_id == "02"
                    )

                elif isinstance(message, MailingVideoContentTypeModel):
                    assert (
                        message.caption == "test video"
                        if index == 0
                        else message.caption is None
                    )
                    assert message.media_group_id == "14035329655475427"
                    assert message.content_type == "video"
                    assert message.file_id == f"00{index+1}"

                else:
                    raise ValueError("тесты не прошли")
