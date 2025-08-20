class BaseError(Exception):
    def __init__(self, message, *args):
        self.message = message
        self.other_args = args


class LoadJsonError(BaseError):
    def __str__(self):
        return f"LoadJsonError: {self.message}. Exception: {self.other_args}"


class AddMailingContentError(BaseError):

    def __str__(self):
        return f"AddMailingContentError: {self.message}. Exception: {self.other_args}"


class CheckMailingContentError(BaseError):
    def __str__(self):
        return f"CheckContentError: {self.message}. Exception: {self.other_args}"


class GetMailingContentError(BaseError):
    def __str__(self):
        return f"GetContentError: {self.message}. Exception: {self.other_args}"


class RemoveMailingContentError(BaseError):
    def __str__(self):
        return f"RemoveContentError: {self.message}. Exception: {self.other_args}"


class UnknownContentType(BaseError):
    def __str__(self):
        return f"UnknownContentType: {self.message}. Exception: {self.other_args}"


class ParseSortError(BaseError):
    def __str__(self):
        return f"ParseSortError: {self.message}. Exception: {self.other_args}"


class AddLastMessageError(BaseError):
    def __str__(self):
        return f"AddLastMessageError: {self.message}. Exception: {self.other_args}"


class GetLastMessageError(BaseError):
    def __str__(self):
        return f"GetLastMessageError: {self.message}. Exception: {self.other_args}"


class CreateUserError(BaseError):
    def __str__(self):
        return f"CreateUserError: {self.message}. Exception: {self.other_args}"


class GetUserError(BaseError):
    def __str__(self):
        return f"GetUserError: {self.message}. Exception: {self.other_args}"


class AddUserError(BaseError):
    def __str__(self):
        return f"AddUserError: {self.message}. Exception: {self.other_args}"


class RemoveUserError(BaseError):
    def __str__(self):
        return f"RemoveUserError: {self.message}. Exception: {self.other_args}"
