from dataclasses import dataclass
from enum import IntEnum
from typing import Optional
from urllib.parse import ParseResult, urlparse

from fetcher.trace import trace


class HttpError(Exception):
    pass


class Status(IntEnum):
    OK = 200


class Request:
    def __init__(self, resource: str):
        url = urlparse(resource)
        if not url.scheme:
            url = urlparse("http://" + resource)

        self.hostname = url.hostname
        self.port = url.port if url.port else 80

        self.data = self._create_request(url)

    @staticmethod
    def _create_request(url: ParseResult) -> bytes:
        method = "GET"
        path = url.path if url.path else "/"

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
        self.status = options.status
        self.status_text = options.status_text
        self.ok = self.status == Status.OK


def parse_response(data: bytes) -> Response:
    if not data:
        msg = "Response is empty"
        raise HttpError(msg)

    prefix, body = data.split(b"\r\n\r\n", maxsplit=1)
    trace("<", prefix)
    trace("<", "\r\n")

    prefix_list = prefix.splitlines()
    start_line = prefix_list[0]
    # headers = prefix_list[1:]

    protocol, status, status_text = start_line.split(b" ", maxsplit=2)

    if protocol != b"HTTP/1.1":
        msg = "Only HTTP/1.1 is supported"
        raise HttpError(msg)

    options = ResponseOptions(status=int(status), status_text=status_text.decode("ascii"))
    return Response(options=options, body=body)
