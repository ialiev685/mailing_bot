from sqlalchemy.orm import Session
import database.controllers as db
from tests.core_testing import *


class TestStartMailing:
    def test_check_start_mailing_without_value(self, session_testing: Session):
        response = db.get_start_mailing_data_impl(session=session_testing)
        assert response is None

    def test_update_value_for_start_mailing(self, session_testing: Session):
        response = db.update_flag_start_mailing_impl(
            value=True, session=session_testing
        )
        assert response.value is True

        response = db.update_flag_start_mailing_impl(
            value=False, session=session_testing
        )
        assert response.value is False
