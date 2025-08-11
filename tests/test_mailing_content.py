from sqlalchemy.orm import Session
import database.controllers as db
from telebot import types
from tests.message_mock import *
from tests.core_testing import *
from helpers import get_formatted_content
import database.controllers as db
from tests.core_testing import *
from tests.message_mock import Message
from object_types import (
    MailingPhotoContentTypeModel,
    MailingTextContentTypeModel,
    MailingContentType,
)


MEDIA_GROUP_ID_ONE = "14035329655475426"

MEDIA_GROUP_ID_TWO = "14035329655475427"


class TestMailingContent:
    def test_add_mailing_content_text_type(self, session_testing: Session):

        message_type_text = Message(content_type="text", text="test")

        formatted_content = get_formatted_content(message=message_type_text)
        if formatted_content:
            db.add_mailing_content_impl(
                content_data=formatted_content, session=session_testing
            )

            sorted_single_content, sorted_group_content = db.get_mailing_content_impl(
                session=session_testing
            )

            assert len(sorted_single_content) == 1
            assert len(sorted_group_content) == 0

            for message in sorted_single_content:
                if isinstance(message, MailingTextContentTypeModel):
                    assert message.text == "test"
                    assert message.media_group_id is None
                    assert message.content_type == "text"
                else:
                    raise ValueError("тесты не прошли")

            return

        raise ValueError

    def test_add_mailing_content_photo_type(self, session_testing: Session):

        message_type_photo = Message(
            content_type="photo", photo_variant_ids=["1", "2", "3", "4"]
        )

        formatted_content = get_formatted_content(message=message_type_photo)

        if formatted_content:
            db.add_mailing_content_impl(
                content_data=formatted_content, session=session_testing
            )

            sorted_single_content, sorted_group_content = db.get_mailing_content_impl(
                session=session_testing
            )

            assert len(sorted_single_content) == 1
            assert len(sorted_group_content) == 0

            for message in sorted_single_content:
                if isinstance(message, MailingPhotoContentTypeModel):
                    assert message.caption is None
                    assert message.media_group_id is None
                    assert message.content_type == "photo"
                    assert message.file_id == "3"
                    assert isinstance(message.file_id, str)

                else:
                    raise ValueError("тесты не прошли")

            return

        raise ValueError("тесты не прошли")

    def test_add_mailing_content_photo_type_with_group(self, session_testing: Session):

        for index in range(0, 4):
            message_type_photo_has_group = Message(
                content_type="photo",
                # разные id файлов для разных размеров - если 4 размера выбирает 3-й, иначе последний
                photo_variant_ids=["1", "2", "3", "4"] if index % 2 == 1 else ["1"],
                media_group_id=MEDIA_GROUP_ID_ONE if index <= 1 else MEDIA_GROUP_ID_TWO,
            )

            formatted_content = get_formatted_content(
                message=message_type_photo_has_group
            )

            if formatted_content:
                db.add_mailing_content_impl(
                    content_data=formatted_content, session=session_testing
                )

        sorted_single_content, sorted_group_content = db.get_mailing_content_impl(
            session=session_testing
        )

        assert len(sorted_single_content) == 0
        assert len(sorted_group_content) == 2

        for index_group, group in enumerate(sorted_group_content.items()):

            key, contents = group

            assert (
                key == MEDIA_GROUP_ID_ONE
                if index_group == 0
                else key == MEDIA_GROUP_ID_TWO
            )

            for index_content, content in enumerate(contents):
                if isinstance(content, MailingPhotoContentTypeModel):

                    assert content.caption is None
                    assert (
                        content.media_group_id == MEDIA_GROUP_ID_ONE
                        if index_group == 0
                        else content.media_group_id == MEDIA_GROUP_ID_TWO
                    )
                    assert content.content_type == "photo"
                    assert (
                        content.file_id == "3"
                        if index_content % 2 == 1
                        else content.file_id == "1"
                    )

                else:
                    raise ValueError("тесты не прошли")
