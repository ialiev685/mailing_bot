import json
from typing import Union
from telebot import types
from error_handlers import LoadJsonError
from object_types import MailingContentTypeModel


def load_json_safe(data_json: str) -> MailingContentTypeModel:
    try:
        return MailingContentTypeModel(**json.loads(data_json))
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


# def save_content_to_json(content_data: list[dict]):
#     try:
#         with open(PATH_MAILING_DATA, "w", encoding="utf-8") as file:
#             json.dump(content_data, file, ensure_ascii=False, indent=4)
#     except Exception as error:
#         print("Ошибка при сохранении контента для рассылки: ", error)


# def add_mailing_data(content: MailingContentTypeModel):

#     try:
#         pass
#         parsed_data = load_json_safe()
#         content_data = content.model_dump()

#         parsed_data.append(content_data)
#         save_content_to_json(parsed_data)

#     except Exception as error:
#         print("Ошибка при добавлении контента для рассылки: ", error)
#         raise
