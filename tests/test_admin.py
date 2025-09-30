import database.controllers as db
from sqlalchemy.orm import Session
from tests.core_testing import *


def generate_about_us_data_in_database(count: int, session: Session):
    for index in range(0, count):
        db.create_about_us_data_impl(
            message_id=4251 + index,
            chat_id=2027691758,
            file_id="01",
            session=session,
            caption="test about us",
        )


class TestAdmin:

    def test_draft_about_us_data(self, session_testing: Session):
        generate_about_us_data_in_database(count=4, session=session_testing)
        about_us_data = db.get_about_us_data_impl(session=session_testing)
        assert about_us_data is None
        about_us_data_draft = db.get_draft_about_us_data_impl(session=session_testing)

        if about_us_data_draft:
            assert len(about_us_data_draft) == 4
        else:
            raise Exception('тест "test_draft_about_us_data" не прошел')

    def test_update_about_us_data(self, session_testing: Session):
        generate_about_us_data_in_database(count=4, session=session_testing)
        about_us_updated = db.update_about_us_data_impl(
            message_id=4252, chat_id=2027691758, session=session_testing
        )
        assert about_us_updated is not None
        about_us_data = db.get_about_us_data_impl(session=session_testing)
        if about_us_data:
            assert about_us_data.chat_id == 2027691758
            assert about_us_data.message_id == 4252
            assert about_us_data.status.value == "ACTIVE"
        else:
            raise Exception('тест "test_update_about_us_data" не прошел')

        about_us_data_draft = db.get_draft_about_us_data_impl(session=session_testing)

        if about_us_data_draft:
            assert len(about_us_data_draft) == 3
        else:
            raise Exception('тест "test_update_about_us_data" не прошел')

    def test_remove_about_us_data_in_current_chat(self, session_testing: Session):
        generate_about_us_data_in_database(count=4, session=session_testing)
        about_us_updated = db.update_about_us_data_impl(
            message_id=4252, chat_id=2027691758, session=session_testing
        )
        assert about_us_updated is not None
        about_us_data = db.get_about_us_data_impl(session=session_testing)
        if about_us_data:
            assert about_us_data.chat_id == 2027691758
            assert about_us_data.message_id == 4252
        else:
            raise Exception(
                'тест "test_remove_about_us_data_from_current_chat" не прошел'
            )

        db.remove_about_us_data_impl(chat_id=2027691758, session=session_testing)
        about_us_data_draft = db.get_draft_about_us_data_impl(session=session_testing)
        assert len(about_us_data_draft) == 0

    def test_change_active_about_us_data(self, session_testing: Session):
        generate_about_us_data_in_database(count=4, session=session_testing)
        db.update_about_us_data_impl(
            message_id=4252, chat_id=2027691758, session=session_testing
        )

        about_us_data = db.get_about_us_data_impl(session=session_testing)
        if about_us_data:
            assert about_us_data.chat_id == 2027691758
            assert about_us_data.message_id == 4252
            assert about_us_data.status.value == "ACTIVE"
        else:
            raise Exception('тест "test_change_active_about_us_data" не прошел')
        db.update_about_us_data_impl(
            message_id=4253, chat_id=2027691758, session=session_testing
        )
        about_us_data = db.get_about_us_data_impl(session=session_testing)
        about_us_data_draft = db.get_draft_about_us_data_impl(session=session_testing)
        if about_us_data:
            assert about_us_data.chat_id == 2027691758
            assert about_us_data.message_id == 4253
            assert about_us_data.status.value == "ACTIVE"
        else:
            raise Exception('тест "test_change_active_about_us_data" не прошел')

        for data in about_us_data_draft:
            assert (
                data.message_id == 4251
                or data.message_id == 4252
                or data.message_id == 4254
            )
            if data.message_id == 4253:
                raise Exception('тест "test_change_active_about_us_data" не прошел')
