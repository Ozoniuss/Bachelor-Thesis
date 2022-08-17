class RequestException(Exception):
    """
    RequestException contains the structure of the errors returned in a request.
    """

    def __init__(self, title, details):
        self.title = title
        self.details = details

    def as_dict(self):
        return {"Title": self.title, "Details": self.details}


class TrainingParametersException(RequestException):
    def __init__(self, details):
        super().__init__("Invalid training parameters", details)


class PaginationParametersException(RequestException):
    def __init__(self, details):
        super().__init__("Invalid pagination parameters", details)


class PostModelBadArguments(RequestException):
    def __init__(self, details):
        super().__init__("Bad model arguments", details)
