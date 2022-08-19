from http import HTTPStatus

bad_request = HTTPStatus.BAD_REQUEST
not_found = HTTPStatus.NOT_FOUND
internal_server_error = HTTPStatus.INTERNAL_SERVER_ERROR


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
            title=bad_request.phrase,
            details=details,
            code=bad_request.value,
        )


class NotFoundException(RequestException):
    def __init__(self, details):
        super().__init__(
            title=not_found.phrase,
            details=details,
            code=not_found.value,
        )


class InternalServerException(RequestException):
    def __init__(self, details):
        super().__init__(
            title=internal_server_error.phrase,
            details=details,
            code=internal_server_error.value,
        )
