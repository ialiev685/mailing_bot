from config import (
    COUNTRIES,
    PREFIX_COUNTRY,
    PREFIX_COUNT_PEOPLE,
    PREFIX_PRICE,
    PREFIX_MONTH,
    PREFIX_SOCIAL,
    PREFIX_DAYS,
    Step,
    STEP_OPTIONS,
    create_callback_data_for_button,
)
import database.controllers as db
from sqlalchemy.orm import Session

from object_types import FieldName

from .message_mock import Message
from handlers.order import (
    get_order_step_options_by_current_step,
    get_updated_data_from_current_step,
)
from helpers import FakeCall, check_valid_phone
from tests.core_testing import *
from typing import TypedDict


class StepDataMock(TypedDict):
    prefix_name: str
    value: str
    field_name: FieldName


mock_button_data_by_call: dict[int, StepDataMock] = {
    Step.step_1.value: {
        "prefix_name": PREFIX_COUNTRY,
        "value": "Москва",
        "field_name": "to_country",
    },
    Step.step_2.value: {
        "prefix_name": PREFIX_COUNT_PEOPLE,
        "value": "4",
        "field_name": "count_people",
    },
    Step.step_3.value: {
        "prefix_name": PREFIX_DAYS,
        "value": "10",
        "field_name": "count_days",
    },
    Step.step_4.value: {
        "prefix_name": PREFIX_MONTH,
        "value": "Май",
        "field_name": "month",
    },
    Step.step_5.value: {
        "prefix_name": PREFIX_PRICE,
        "value": "400 000р",
        "field_name": "price",
    },
    Step.step_6.value: {
        "prefix_name": PREFIX_SOCIAL,
        "value": "Telegram",
        "field_name": "connection",
    },
}


class TestOrder:
    def test_start_create_order(self, session_testing: Session):
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
            object_call = FakeCall(
                message=Message(content_type="text", text="", user_id=2027691758),
                data=create_callback_data_for_button(
                    step=order.current_step,
                    prefix_name=PREFIX_COUNTRY,
                    value=COUNTRIES[0],
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

    def test_create_order_from_start_to_finish(self, session_testing: Session):

        created_order = db.create_order_impl(
            user_id=2027691758, session=session_testing
        )
        assert created_order.current_step == 1
        assert created_order.to_country is None
        for index in range(0, len(Step)):
            step = index + 1
            order = db.get_order_data_by_user_id_impl(
                user_id=2027691758, session=session_testing
            )

            if order:

                prefix_name = mock_button_data_by_call[step]["prefix_name"]
                value = mock_button_data_by_call[step]["value"]
                field_name = mock_button_data_by_call[step]["field_name"]

                object_call = FakeCall(
                    message=Message(content_type="text", text="", user_id=2027691758),
                    data=create_callback_data_for_button(
                        step=step,
                        prefix_name=prefix_name,
                        value=value,
                    ),
                )
                updated_data = get_updated_data_from_current_step(
                    call=object_call,
                    order=order,
                    prefix=prefix_name,
                    field_name=field_name,
                )

                db.update_order_data_by_step_impl(
                    session=session_testing, **updated_data
                )
                order_after_update = db.get_order_data_by_user_id_impl(
                    user_id=2027691758, session=session_testing
                )
                next_step = order_after_update.current_step
                if order_after_update:

                    if next_step == 2:
                        assert order.to_country == "Москва"
                        assert order.count_people is None
                        assert order.count_days is None
                        assert order.month is None
                        assert order.price is None
                        assert order.connection is None
                        assert order.is_created_order is False
                    elif next_step == 3:
                        assert order.to_country == "Москва"
                        assert order.count_people == "4"
                        assert order.count_days is None
                        assert order.month is None
                        assert order.price is None
                        assert order.connection is None
                        assert order.is_created_order is False
                    elif next_step == 4:
                        assert order.to_country == "Москва"
                        assert order.count_people == "4"
                        assert order.count_days == "10"
                        assert order.month is None
                        assert order.price is None
                        assert order.connection is None
                        assert order.is_created_order is False
                    elif next_step == 5:
                        assert order.to_country == "Москва"
                        assert order.count_people == "4"
                        assert order.count_days == "10"
                        assert order.month == "Май"
                        assert order.price is None
                        assert order.connection is None
                        assert order.is_created_order is False
                    elif next_step == 6:
                        assert order.to_country == "Москва"
                        assert order.count_people == "4"
                        assert order.count_days == "10"
                        assert order.month == "Май"
                        assert order.price == "400 000р"
                        assert (
                            order.connection == "Telegram"
                            if order.is_created_order is True
                            else order.connection is None
                        )
                        assert (
                            order.is_created_order is True
                            if order.connection == "Telegram"
                            else order.is_created_order is False
                        )
                    else:
                        raise Exception(
                            'тест "test_create_order_from_start_to_finish" не прошел'
                        )

                else:
                    raise Exception(
                        'тест "test_create_order_from_start_to_finish" не прошел'
                    )

            else:
                raise Exception(
                    'тест "test_create_order_from_start_to_finish" не прошел'
                )

    def test_valid_phone_number(self):
        phones_variants = [
            "+79999999999",
            "79999999999",
            "89999999999",
            "9234567890",
            "1234567890",
            "2234567890",
            "3234567890",
            "4234567890",
            "5234567890",
            "6234567890",
            "7234567890",
            "8234567890",
            "9234567890",
            "+13234567890",
            "+2234567890",
            "+33234567890",
            "+43234567890",
            "+53234567890",
            "+63234567890",
            "+73234567890",
            "+83234567890",
            "+93234567890",
        ]

        for phone in phones_variants:
            assert check_valid_phone(phone) is True
