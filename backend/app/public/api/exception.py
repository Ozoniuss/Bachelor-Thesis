from http import HTTPStatus

BAD_REQUEST = HTTPStatus.BAD_REQUEST


class RequestException:
    """
    RequestException contains the structure of the errors returned in a request.
    """

    def __init__(self, title, details, code):
        self.title = title
        self.details = details
        self.code = code

    def as_dict(self):
        return {"Title": self.title, "Details": self.details}


class BadRequestException(RequestException):
    def __init__(self, details):
        super().__init__(
            title=BAD_REQUEST.phrase,
            details=details,
            code=BAD_REQUEST.value,
        )
