from collections import namedtuple
from random import choice
from typing import Dict, Optional, Protocol

from pydantic import BaseModel, model_validator

CropParams: namedtuple = namedtuple("MeteoBlueCrop", "top, right, bottom, left")
Coords2Points = namedtuple("Coords2Points", "act_x, act_y")
UmMeteoGram = namedtuple("UmMeteoGram", "base_img, extra_img")


class RequestHeadersProtocol(Protocol):
    """Request headers protocol"""

    def dict(self, **kwargs) -> Dict:
        raise NotImplementedError

    def to_list(self, key: Optional[str] = None):
        raise NotImplementedError


ORIGIN: str = ""

USER_AGENTS: list = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 "
    "Safari/537.36 Edge/14.14393",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 "
    "Mobile/14E304 Safari/602.1",
]


class RequestHeaders(BaseModel):
    """Headers params"""

    user_agent: Optional[str] = None
    origin: str = ORIGIN
    accept: str = "application/json, text/plain, */*"
    accept_encoding: str = "gzip, deflate, br"
    accept_language: str = "en-US,en;q=0.9,pl;q=0.8"
    method: str = "GET"

    @staticmethod
    def user_agents() -> list[str]:
        """Interface to user agents list."""
        return USER_AGENTS

    @model_validator(mode="before")  # noqa
    @classmethod
    def validate_data(cls, data: dict) -> dict:
        """call different user agent on every object call"""
        data["user_agent"] = choice(cls.user_agents())
        return data

    def dict(self, **kwargs) -> Dict:
        """serialize headers"""
        serialized = super().model_dump()
        serialized["User-agent"] = serialized.pop("user_agent")
        return serialized

    def to_list(self, key: Optional[str] = None) -> list[tuple[str, str]]:
        """serialize headers to list"""
        return [
            (dict_key, val)
            for dict_key, val in self.dict().items()
            if key is None or dict_key.lower() == key.lower()
        ]
