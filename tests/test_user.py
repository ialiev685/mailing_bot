from sqlalchemy.orm import Session
import database.controllers.user as db
from object_types import RoleEnum

from tests.core_testing import *

from sqlalchemy.orm import Session


def generate_user_by_number_in_database(count: int, session: Session):
    for index in range(0, count):
        db.create_user_impl(
            user_id=index + 1,
            first_name="user",
            chat_id=index + 1,
            role=RoleEnum.USER,
            session=session,
        )


class TestUser:
    def test_create_user(self, session_testing: Session):

        user = db.create_user_impl(
            user_id=1,
            first_name="user",
            chat_id=1,
            role=RoleEnum.USER,
            session=session_testing,
        )

        assert user.user_id == 1
        assert user.first_name == "user"
        assert user.last_name is None
        assert user.role == RoleEnum.USER
        assert user.subscriber.chat_id == 1
        assert user.subscriber.signed == True

    def test_get_user(self, session_testing: Session):

        first_response_user = db.get_user_impl(user_id=1, session=session_testing)

        assert first_response_user is None

        db.create_user_impl(
            user_id=1,
            first_name="user",
            chat_id=1,
            role=RoleEnum.USER,
            session=session_testing,
        )

        two_response_user = db.get_user_impl(user_id=1, session=session_testing)

        assert two_response_user.user_id == 1
        assert two_response_user.first_name == "user"
        assert two_response_user.last_name is None
        assert two_response_user.role == RoleEnum.USER
        assert two_response_user.subscriber.chat_id == 1
        assert two_response_user.subscriber.signed == True

    def test_get_users(self, session_testing: Session):

        first_response_users = db.get_users_impl(session=session_testing)

        assert isinstance(first_response_users, list) is True

        generate_user_by_number_in_database(count=4, session=session_testing)

        two_response_users = db.get_users_impl(session=session_testing)

        for index, user in enumerate(two_response_users):
            assert user.user_id == index + 1
            assert user.signed is True
            assert user.chat_id == index + 1

            assert user.user.user_id == index + 1
            assert user.user.first_name == "user"
            assert user.user.last_name is None
            assert user.user.role == RoleEnum.USER
            assert user.user.subscriber.chat_id == index + 1
            assert user.user.subscriber.signed == True
