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


class UnknownContentType(BaseError):
    def __str__(self):
        return f"UnknownContentType: {self.message}. Exception: {self.other_args}"


class ParseSortError(BaseError):
    def __str__(self):
        return f"ParseSortError: {self.message}. Exception: {self.other_args}"


class AddLastMessageError(BaseError):
    def __str__(self):
        return f"AddLastMessageError: {self.message}. Exception: {self.other_args}"
