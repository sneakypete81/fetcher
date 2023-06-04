from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List, Optional
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


class ResponseParser:
    def __init__(self):
        self.finished = False
        self._in_body = False
        self._prefix = bytes([])
        self._body = bytes([])
        self._options = ResponseOptions()

    def push_fragment(self, data: bytes) -> None:
        if self._in_body:
            self._push_body_fragment(data)
        else:
            self._push_prefix_fragment(data)

    def response(self) -> Response:
        return Response(options=self._options, body=self._body)

    def _push_prefix_fragment(self, data: bytes) -> None:
        self._prefix += data

        if b"\r\n\r\n" in self._prefix:
            self._in_body = True
            self._prefix, body_data = self._prefix.split(b"\r\n\r\n", maxsplit=1)

            self._options = _parse_prefix(self._prefix)
            self._push_body_fragment(body_data)

    def _push_body_fragment(self, data: bytes) -> None:
        self._body += data
        self.finished = _finished_parsing(headers=self._options.headers, body=self._body)


def _parse_prefix(prefix) -> ResponseOptions:
    trace("<", prefix)
    trace("<", "\r\n")

    prefix_list = prefix.splitlines()
    start_line = prefix_list[0]
    headers = _parse_headers(prefix_list[1:])

    protocol, status, status_text = start_line.split(b" ", maxsplit=2)

    if protocol != b"HTTP/1.1":
        msg = "Only HTTP/1.1 is supported"
        raise HttpError(msg)

    return ResponseOptions(status=int(status), status_text=status_text.decode("ascii"), headers=headers)


def _parse_headers(lines: List[bytes]) -> Dict[str, str]:
    headers = {}
    for line in lines:
        key, value = line.split(b":", maxsplit=1)
        headers[key.strip().decode("ascii")] = value.strip().decode("ascii")

    return headers


def _finished_parsing(headers, body):
    if "Content-Length" in headers:
        if len(body) >= int(headers["Content-Length"]):
            return True
    return False
