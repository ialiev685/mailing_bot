from sqlalchemy.orm import Session
import database.controllers as db
from object_types import RoleEnum
from tests.core_testing import *


def generate_user_by_number_in_database(count: int, session: Session):
    for index in range(0, count):
        db.create_user_impl(
            user_id=2027691758 + index,
            first_name="user",
            chat_id=2027691758 + index,
            role=RoleEnum.USER,
            session=session,
        )


class TestUser:
    def test_create_user(self, session_testing: Session):
        user = db.create_user_impl(
            user_id=2027691758,
            first_name="user",
            chat_id=2027691758,
            role=RoleEnum.USER,
            session=session_testing,
        )

        assert user.user_id == 2027691758
        assert user.first_name == "user"
        assert user.last_name is None
        assert user.role == RoleEnum.USER
        assert user.subscriber.chat_id == 2027691758
        assert user.subscriber.signed == True

    def test_get_user(self, session_testing: Session):
        first_response_user = db.get_user_impl(
            user_id=2027691758, session=session_testing
        )

        assert first_response_user is None

        generate_user_by_number_in_database(count=4, session=session_testing)

        two_response_user = db.get_user_impl(
            user_id=2027691760, session=session_testing
        )

        assert two_response_user.user_id == 2027691760
        assert two_response_user.first_name == "user"
        assert two_response_user.last_name is None
        assert two_response_user.role == RoleEnum.USER
        assert two_response_user.subscriber.chat_id == 2027691760
        assert two_response_user.subscriber.signed == True

    def test_get_users(self, session_testing: Session):
        first_response_users = db.get_users_impl(session=session_testing)
        assert isinstance(first_response_users, list) is True

        generate_user_by_number_in_database(count=4, session=session_testing)
        two_response_users = db.get_users_impl(session=session_testing)
        assert len(two_response_users) == 4

    def test_unsubscribe_user(self, session_testing: Session):
        generate_user_by_number_in_database(count=4, session=session_testing)
        users = db.get_users_impl(session=session_testing)
        assert len(users) == 4
        db.unsubscribe_user_impl(user_id=2027691761, session=session_testing)
        user = db.get_user_impl(user_id=2027691761, session=session_testing)
        assert user is None
        users = db.get_users_impl(session=session_testing)
        assert len(users) == 3

    def test_count_subscribed_users(self, session_testing: Session):
        generate_user_by_number_in_database(count=4, session=session_testing)
        count = db.get_count_users_impl(session=session_testing)
        assert count == 4
        db.unsubscribe_user_impl(user_id=2027691759, session=session_testing)
        count = db.get_count_users_impl(session=session_testing)
        assert count == 3
