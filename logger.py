import logging
import os
import sys
from datetime import datetime
from typing import Optional

from settings import settings


class ColoredFormatter(logging.Formatter):
    default_msec_format: str = "%s"

    @staticmethod
    def message_formatter() -> str:
        """Custom message formatter"""

        return "%(asctime)s [%(name)s] - [%(levelname)s] - %(message)s (%(filename)s:%(lineno)d)"

    @property
    def colours(self) -> dict:
        """Custom logger level colour formatter"""

        return {
            "DEBUG": self.grey + self.message_formatter() + self.reset,
            "INFO": self.green + self.message_formatter() + self.reset,
            "WARNING": self.red + self.message_formatter() + self.reset,
            "ERROR": self.red + self.message_formatter() + self.reset,
            "CRITICAL": self.bold_red + self.message_formatter() + self.reset,
            "WELCOME_MSG": self.welcome
            + self.message_formatter().replace("(%(filename)s:%(lineno)d)", "")
            + self.reset,
        }

    def __init__(self, use_color=True):
        logging.Formatter.__init__(self)
        self.use_color = use_color
        self.grey: str = "\x1b[38;20m"
        self.blue: str = "\x1b[38;5;39m"
        self.yellow: str = "\x1b[33;20m"
        self.red: str = "\x1b[31;20m"
        self.bold_red: str = "\x1b[31;1m"
        self.green: str = "\x1b[38;5;190m"
        self.welcome: str = "\x1b[38;5;222m"

        self.reset: str = "\x1b[0m"

    def format(self, record) -> str:
        colour: Optional[str] = self.colours.get(record.levelname)
        formatter: logging.Formatter = logging.Formatter(colour)
        return formatter.format(record)


class ColoredLogger(logging.Logger):
    """Custom logger with extra levels"""

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)
        logging.addLevelName(90, "WELCOME_MSG")

        color_formatter: ColoredFormatter = ColoredFormatter()

        console: logging.StreamHandler = logging.StreamHandler()
        console.setFormatter(color_formatter)

        log_dir: str = os.path.join(settings.ROOT_PATH, "logs")
        file_handler: logging = logging.FileHandler(
            f"{log_dir}/{datetime.now().date()}.log", encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)

        formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s"
        )
        file_handler.setFormatter(formatter)

        self.addHandler(console)
        self.addHandler(file_handler)
        # self.addHandler(logging.FileHandler(f"{log_dir}/{datetime.now().date()}.log"))
        self.setLevel(logging.INFO)
        return

    def welcome_msg(self, msg, *args, **kw) -> None:
        """Custom logger level"""

        self.log(90, msg, *args, **kw)


def get_module_logger(mod_name: str) -> ColoredLogger:
    """
    returns logger. Example usage:
    logger = get_module_logger('name')
    """
    logging.setLoggerClass(ColoredLogger)
    return logging.getLogger(mod_name)  # type: ignore


# get_module_logger("TESTING_LOGGER").welcome_msg("Welcome")


class ExceptionTypeFormatter(logging.Formatter):
    def format(self, record):
        if record.exc_info:
            exc_type = record.exc_info[0].__name__  # Extract the exception type
            record.msg = f"{exc_type}"  # Set only the exception type as the message
        return super().format(record)


def configure_unhandled_exceptions_logger() -> logging.Logger:
    """Add a file/console handler for unhandled exceptions to the logger"""

    unhandled_exceptions_logger = logging.getLogger("ExceptionLogger")
    unhandled_exceptions_logger.setLevel(logging.ERROR)
    log_dir: str = os.path.join(settings.ROOT_PATH, "logs")

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    if not os.path.exists(f"{log_dir}/unhandled_exception"):
        os.mkdir(f"{log_dir}/unhandled_exception")

    # Create a file handler for unhandled exceptions
    file_log_path: str = f"{log_dir}/unhandled_exception/{datetime.now().date()}.log"
    file_handler_unhandled = logging.FileHandler(file_log_path)
    file_handler_unhandled.setLevel(logging.ERROR)

    # Create a console handler for unhandled exceptions
    console_handler_unhandled = logging.StreamHandler()
    console_handler_unhandled.setLevel(logging.ERROR)

    # Create a formatter for the unhandled exceptions
    string_format: str = (
        "%(asctime)s [%(name)s] %(levelname)s: %(message)s in %(filename)s:%(lineno)d"
    )
    formatter_unhandled = ExceptionTypeFormatter(string_format)
    file_handler_unhandled.setFormatter(formatter_unhandled)
    console_handler_unhandled.setFormatter(formatter_unhandled)

    # Create a colored formatter for console handler
    colored_formatter = ColoredFormatter(use_color=True)

    # Set the formatter for console handler
    console_handler_unhandled.setFormatter(colored_formatter)

    # Add the file handler for unhandled exceptions to the logger
    unhandled_exceptions_logger.addHandler(file_handler_unhandled)
    unhandled_exceptions_logger.addHandler(console_handler_unhandled)

    return unhandled_exceptions_logger


def exception_handler(exc_type, exc_value, exc_traceback) -> None:
    """Set the custom exception handler for unhandled exceptions"""
    unhandled_exceptions_logger = configure_unhandled_exceptions_logger()

    # Extract the exception type and its message
    exception_name = exc_type.__name__ if exc_type else ""
    exception_message = str(exc_value) if exc_value else ""

    # Construct the message for the console handler
    console_message = f"{exception_name}: {exception_message}"

    # Log the constructed message with the console handler
    unhandled_exceptions_logger.error(
        console_message, exc_info=(exc_type, exc_value, exc_traceback)
    )


# Set the custom exception handler
sys.excepthook = exception_handler
