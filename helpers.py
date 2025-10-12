import json
import re
from typing import Union, Callable, Type, Optional, Any
from telebot import types
from error_handlers import LoadJsonError, UnknownContentType, ParseSortError
from object_types import (
    MailingTextContentTypeModel,
    MailingPhotoContentTypeModel,
    MailingVideoContentTypeModel,
    MailingContentType,
)
from database.models import MailingContentModel
from telebot import types
from database.core import engine
from sqlalchemy.orm import Session
import error_handlers as error_instance
import logging


logger = logging.getLogger(__name__)


def load_json_safe(data_json: str) -> MailingContentType:
    try:
        parsed_content = json.loads(data_json)

        models = {
            "text": MailingTextContentTypeModel,
            "photo": MailingPhotoContentTypeModel,
            "video": MailingVideoContentTypeModel,
        }

        content_type = None

        if isinstance(parsed_content, dict) and parsed_content.get("content_type"):
            content_type = parsed_content.get("content_type")

        if content_type is not None:
            return models[content_type](**parsed_content)

        raise UnknownContentType("Неизвестный тип контента при парсинге json данных")

    except UnknownContentType as error:
        raise UnknownContentType(error.message)

    except Exception as error:
        raise LoadJsonError("Ошибка при парсинге контента из json", error)


def get_optimal_photo(
    photo_list: list[types.PhotoSize],
) -> types.PhotoSize:
    photo = None
    if isinstance(photo_list, list) and len(photo_list) >= 3:
        photo = photo_list[2]
    else:
        photo = photo_list[-1]

    return photo


def get_formatted_content(
    message: types.Message,
) -> Union[
    MailingContentType,
    None,
]:

    if message.content_type == "text":
        return MailingTextContentTypeModel(content_type="text", text=message.text)
    if message.content_type == "photo":
        return MailingPhotoContentTypeModel(
            content_type="photo",
            file_id=get_optimal_photo(message.photo).file_id,
            media_group_id=message.media_group_id,
            caption=message.caption,
        )
    if message.content_type == "video":

        return MailingVideoContentTypeModel(
            content_type="video",
            file_id=message.video.file_id,
            media_group_id=message.media_group_id,
            caption=message.caption,
        )

    return None


def parse_and_sort_content(str_content_list: list[MailingContentModel]):

    sorted_group_content: dict[
        str, Union[MailingContentType, list[MailingContentType]]
    ] = {}

    try:

        for index, item in enumerate(str_content_list):

            parsed_content = load_json_safe(item.content)
            content_type = parsed_content.content_type
            media_group_id = parsed_content.media_group_id

            if content_type == "text":
                sorted_group_content[str(index)] = parsed_content
            elif (
                content_type == "photo" or content_type == "video"
            ) and parsed_content.media_group_id is None:
                sorted_group_content[str(index)] = parsed_content
            elif (
                content_type == "photo" or content_type == "video"
            ) and media_group_id is not None:

                if media_group_id in sorted_group_content:
                    existing_value = sorted_group_content[media_group_id]
                    if isinstance(existing_value, list):
                        existing_value.append(parsed_content)
                else:
                    sorted_group_content[media_group_id] = [parsed_content]

        return sorted_group_content
    except Exception as error:
        raise ParseSortError("Ошибка при сортировки контента: ", error)


def create_media_group(content_list: list[MailingContentType]):

    media: list[Union[types.InputMediaPhoto, types.InputMediaVideo]] = []
    caption = None

    for content in content_list:
        if content.content_type == "video" or content.content_type == "photo":
            if content.caption:
                caption = content.caption
                break

    for index, content in enumerate(content_list):

        if content.content_type == "photo":
            media.append(
                types.InputMediaPhoto(
                    media=content.file_id,
                    caption=caption if index == 0 else None,
                    parse_mode="Markdown" if index == 0 else None,
                )
            )
        elif content.content_type == "video":
            media.append(
                types.InputMediaVideo(
                    media=content.file_id,
                    caption=caption if index == 0 else None,
                    parse_mode="Markdown" if index == 0 else None,
                )
            )
    return media


def session_decorator(errorInstance: Type[Exception], errorMessage: str):
    def decorator(callback: Callable):
        def wrapper(*args, **kwargs):
            try:
                with Session(engine) as session:
                    return callback(*args, **kwargs, session=session)
            except Exception as error:
                session.rollback()
                raise errorInstance(errorMessage, error)

        return wrapper

    return decorator


def handler_error_decorator(
    callBack: Optional[Callable] = None,
    func_name: str = "unknown",
):
    def decorator(callback: Callable):
        def wrapper(*args, **kwargs):

            error_classes = (
                error_instance.AddMailingContentError,
                error_instance.AddUserError,
                error_instance.CheckMailingContentError,
                error_instance.CreateUserError,
                error_instance.GetUserError,
                error_instance.GetMailingContentError,
                error_instance.LoadJsonError,
                error_instance.RemoveUserError,
                error_instance.RemoveMailingContentError,
                error_instance.ParseSortError,
                error_instance.UnknownContentType,
                error_instance.StartMailingError,
            )

            try:
                # logger.info(
                #     "callback name: %s", func_name, extra={"func_name": func_name}
                # )
                return callback(*args, **kwargs)
            except error_classes as error:
                if callBack is not None:
                    callBack(*args, **kwargs)
                logger.error(error, extra={"func_name": func_name})
            except Exception as error:
                if callBack is not None:
                    callBack(*args, **kwargs)
                logger.error(error, extra={"func_name": func_name})

        return wrapper

    return decorator


def has_value_in_data_name(value: str) -> Callable:
    def callback(query: Any) -> bool:
        if isinstance(query, types.CallbackQuery):
            return (
                hasattr(query, "data")
                and isinstance(query.data, str)
                and query.data.startswith(value)
            )

        return False

    return callback


def check_valid_phone(text: str) -> bool:
    is_valid_phone = re.match(
        r"^(\+7|7|8)?[\s\-\(\)]*9\d{2}[\s\-\(\)]*\d{3}[\s\-\(\)]*\d{2}[\s\-\(\)]*\d{2}$",
        text,
    )
    return bool(is_valid_phone)


def create_fake_object_call(message: types.Message, data: str):
    # имитация вызова кнопки
    class FakeCall:
        def __init__(self, message: types.Message):
            self.id = "fake_call_id"
            self.message = message
            self.data = data
            self.from_user = message.from_user

    return FakeCall(message=message)


def find_data_link_from_text(text: str) -> tuple[str, str] | None:
    pattern = r"\[(.*?)\]\((.*?)\)"
    result = re.search(pattern, text)

    if result:
        url = result.group(1)
        name = result.group(2)
        return (url, name)
    return None
