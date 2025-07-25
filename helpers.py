import json
from typing import Union, Callable, Type
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
from collections import defaultdict
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
    photo_list: Union[list[types.PhotoSize], None],
) -> types.PhotoSize:
    photo = None
    if photo_list:
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
    sorted_single_content: list[MailingContentType] = []
    sorted_group_content: dict[str, list[MailingContentType]] = defaultdict(list)

    try:

        for item in str_content_list:

            parsed_content = load_json_safe(item.content)
            content_type = parsed_content.content_type
            media_group_id = parsed_content.media_group_id

            if content_type == "text":
                sorted_single_content.append(parsed_content)
            if (
                content_type == "photo" or content_type == "video"
            ) and parsed_content.media_group_id is None:
                sorted_single_content.append(parsed_content)
            if (
                content_type == "photo" or content_type == "video"
            ) and media_group_id is not None:
                sorted_group_content[media_group_id].append(parsed_content)

        return (sorted_single_content, sorted_group_content)
    except Exception as error:
        raise ParseSortError("Ошибка при сортировки контента: ", error)


def create_media_group(
    content_list: list[MailingContentType],
    input: Union[types.InputMediaPhoto, types.InputMediaVideo],
):
    media: list[Union[types.InputMediaPhoto, types.InputMediaVideo]] = []
    caption = None

    for content in content_list:
        if content.content_type == "video" or content.content_type == "photo":
            caption = content.caption
            break

    for index, content in enumerate(content_list):
        if content.content_type == "video" or content.content_type == "photo":
            media.append(
                input(
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
            except errorInstance as error:
                session.rollback()
                raise errorInstance(errorMessage, error)
            except Exception as error:
                session.rollback()
                raise Exception("Произошла неизвестная ошибка при работе с БД", error)

        return wrapper

    return decorator


def handler_error_decorator(callback: Callable):
    def wrapper(*args, **kwargs):

        error_classes = (
            error_instance.AddLastMessageError,
            error_instance.AddMailingContentError,
            error_instance.AddUserError,
            error_instance.CheckMailingContentError,
            error_instance.CreateUserError,
            error_instance.GetLastMessageError,
            error_instance.GetUserError,
            error_instance.GetMailingContentError,
            error_instance.LoadJsonError,
            error_instance.RemoveUserError,
            error_instance.RemoveLastMessageError,
            error_instance.RemoveMailingContentError,
            error_instance.ParseSortError,
            error_instance.UnknownContentType,
        )

        try:
            return callback(*args, **kwargs)
        except error_classes as error:
            logger.error(error)
        except Exception as error:
            logger.error(error)

    return wrapper
