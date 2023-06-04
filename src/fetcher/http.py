from dataclasses import dataclass
from enum import IntEnum
from typing import Optional
from urllib.parse import ParseResult, urlparse


class Status(IntEnum):
    OK = 200


class Request:
    def __init__(self, resource: str):
        url = urlparse(resource)
        if not url.scheme:
            url = urlparse("http://" + resource)

        self.hostname = url.hostname
        self.port = url.port

        self.data = self._create_request(url)

    @staticmethod
    def _create_request(url: ParseResult) -> bytes:
        method = "GET"
        path = "/" if not url.path else url.path

        data = f"{method} {path} HTTP/1.1\r\n"
        data += f"Host: {url.hostname}\r\n"
        data += "\r\n"

        return data.encode("ascii")


@dataclass
class ResponseOptions:
    status: int = Status.OK
    status_text: str = ""


class Response:
    def __init__(self, body: bytes = b"", options: Optional[ResponseOptions] = None):
        if not options:
            options = ResponseOptions()

        self.body = body
        self.ok = options.status == Status.OK
        self.status_text = options.status_text


def parse_response(data: bytes) -> Response:
    lines = data.splitlines()
    protocol, status, status_text = lines[0].split(b" ", maxsplit=2)

    if protocol != b"HTTP/1.1":
        msg = "Only 'HTTP/1.1' is supported"
        raise ValueError(msg)

    options = ResponseOptions(status=int(status), status_text=status_text.decode("ascii"))
    return Response(options=options)
