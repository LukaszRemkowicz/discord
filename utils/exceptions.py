from asyncpg import CannotConnectNowError


class CustomBaseException(Exception):
    default_message: str = ""

    def __init__(self):
        super().__init__(self.default_message)


class DriverException(CustomBaseException):
    default_message: str = "Driver occurred problem"


class TestDBWrongCredentialsError(CustomBaseException):
    default_message = "Credentials for test DB are wrong. " \
                      "Please be sure that you have valid variables in .env file in root directory"


class DBConnectionError(ConnectionError, CannotConnectNowError):
    default_message = str(CannotConnectNowError)


class NoImageFoundException(Exception):
    default_message = "Image could not be found. Check if path exists"


class UploadToNotGivenException(Exception):
    default_message = "Parameter upload_to not given. Be sure you used it in FileField field"
