import database.controllers as db
from sqlalchemy.orm import Session
from tests.core_testing import *


class TestLastMessage:
    def test_add_first_last_message(self, session_testing: Session):
        db.add_last_message_impl(
            chat_id=1, text="test description", message_id=1, session=session_testing
        )

        last_message = db.get_last_message_impl(chat_id=1, session=session_testing)

        assert last_message.message_id == 1
        assert last_message.chat_id == 1
        assert last_message.text == "test description"

    def test_add_next_last_message(self, session_testing: Session):
        db.add_last_message_impl(
            chat_id=1, text="test description 1", message_id=1, session=session_testing
        )
        db.add_last_message_impl(
            chat_id=1, text="test description 2", message_id=2, session=session_testing
        )
        last_message = db.get_last_message_impl(chat_id=1, session=session_testing)
        all_messages = db.get_last_messages_impl(session=session_testing)

        assert last_message.message_id == 2
        assert last_message.chat_id == 1
        assert last_message.text == "test description 2"
        assert len(all_messages) == 1
