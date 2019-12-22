from abc import ABC
from enum import unique, Enum
from http import HTTPStatus


@unique
class AppErrorCodes(Enum):
    """Enum for HTTP Error Codes"""

    INVALID_INPUT = 3
    GOOGLE_MAPS_ERROR = 5
    SERVICE_NOT_AVAILABLE = 6
    DB_OPERATION_FAILED = 7
    STATION_NOT_FOUND = 8


class TranJerseyException(Exception, ABC):
    HTTP_CODE = HTTPStatus.INTERNAL_SERVER_ERROR.value

    def __init__(self, error_code: AppErrorCodes, message):
        super().__init__(message)
        self.error_code = error_code
        self.message = message

    def to_dict(self):
        return {
            "error_code": self.error_code.name,
            "error_message": self.message
        }


class InputValidationException(TranJerseyException):
    HTTP_CODE = HTTPStatus.UNPROCESSABLE_ENTITY.value

    def __init__(self, error_code: AppErrorCodes, message: str):
        super().__init__(error_code, message)


class NjTransitException(TranJerseyException):
    HTTP_CODE = HTTPStatus.FAILED_DEPENDENCY.value

    def __init__(self, error_code: AppErrorCodes, message: str):
        super().__init__(error_code, message)


class DBConnectionFailure(TranJerseyException):
    HTTP_CODE = HTTPStatus.FAILED_DEPENDENCY.value

    def __init__(self, error_code: AppErrorCodes, message: str):
        super().__init__(error_code, message)
