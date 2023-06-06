from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, Optional


class Status(IntEnum):
    OK = 200


@dataclass
class ResponseOptions:
    status: int = Status.OK
    status_text: str = ""
    headers: Dict[str, str] = field(default_factory=dict)


class Response:
    def __init__(self, body: bytes = b"", options: Optional[ResponseOptions] = None):
        if not options:
            options = ResponseOptions()

        self.body = body
        self.headers = options.headers
        self.status = options.status
        self.status_text = options.status_text
        self.ok = self.status == Status.OK
