from config import (
    COUNTRIES,
    PREFIX_COUNTRY,
    Step,
    STEP_OPTIONS,
    create_callback_data_for_button,
)
import database.controllers as db
from sqlalchemy.orm import Session

from .message_mock import Message
from handlers.order import (
    get_order_step_options_by_current_step,
    get_updated_data_from_current_step,
)
from helpers import create_fake_object_call
from tests.core_testing import *


class TestOrder:
    def test_create_order(self, session_testing: Session):
        created_order = db.create_order_impl(
            user_id=2027691758, session=session_testing
        )
        assert created_order.is_created_order is False
        assert created_order.user_id == 2027691758

        order = db.get_order_data_by_user_id_impl(
            user_id=2027691758, session=session_testing
        )
        if order:
            assert order.is_created_order is False
            assert order.user_id == 2027691758
            options = get_order_step_options_by_current_step(
                current_step=order.current_step
            )
            if options:
                assert options["count_steps"] == len(Step)
                assert options["options"]["title"] == STEP_OPTIONS[1]["title"]
            else:
                raise Exception('тест "test_create_order" не прошел')

        else:
            raise Exception('тест "test_create_order" не прошел')

    def test_next_step(self, session_testing: Session):

        db.create_order_impl(user_id=2027691758, session=session_testing)
        order = db.get_order_data_by_user_id_impl(
            user_id=2027691758, session=session_testing
        )
        if order:
            object_call = create_fake_object_call(
                message=Message(content_type="text", text="", user_id=2027691758),
                data=create_callback_data_for_button(
                    step=order.current_step,
                    prefix_name=PREFIX_COUNTRY,
                    name=COUNTRIES[0],
                ),
            )
            updated_data = get_updated_data_from_current_step(
                call=object_call,
                order=order,
                prefix=PREFIX_COUNTRY,
                field_name="to_country",
            )

            db.update_order_data_by_step_impl(session=session_testing, **updated_data)
            order = db.get_order_data_by_user_id_impl(
                user_id=2027691758, session=session_testing
            )
            if not order:
                raise Exception('тест "test_next_step" не прошел')

            assert order.current_step == 2
            assert order.to_country == COUNTRIES[0]

        else:
            raise Exception('тест "test_next_step" не прошел')
