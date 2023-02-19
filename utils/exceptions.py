class CustomBaseException(Exception):
    default_message: str = ""

    def __init__(self):
        super().__init__(self.default_message)


class DriverException(CustomBaseException):
    default_message: str = "Driver occurred problem"
