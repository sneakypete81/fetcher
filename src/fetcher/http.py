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
        self._prefix_parser = PrefixParser()
        self._body_parser = ContentLengthBodyParser({})
        self._options = ResponseOptions()

    def push_fragment(self, data: bytes) -> None:
        if self._prefix_parser.finished:
            self._body_parser.push(data)
        else:
            self._push_prefix_fragment(data)

    def finished(self) -> bool:
        return self._body_parser.finished()

    def response(self) -> Response:
        return Response(options=self._options, body=self._body_parser.body)

    def _push_prefix_fragment(self, data: bytes) -> None:
        self._prefix_parser.push(data)
        if self._prefix_parser.finished:
            self._options = self._prefix_parser.options()
            self._body_parser = ContentLengthBodyParser(self._options.headers)
            self._body_parser.push(self._prefix_parser.body_fragment)


class PrefixParser:
    def __init__(self):
        self.prefix = b""
        self.finished = False
        self.body_fragment = b""

    def push(self, data: bytes):
        prefix = self.prefix + data
        if b"\r\n\r\n" not in prefix:
            self.prefix = prefix
            return

        self.prefix, self.body_fragment = prefix.split(b"\r\n\r\n", maxsplit=1)
        self.finished = True
        trace("<", self.prefix)
        trace("<", "\r\n")

    def options(self) -> ResponseOptions:
        prefix_list = self.prefix.splitlines()
        start_line = prefix_list[0]
        headers = self._parse_headers(prefix_list[1:])

        protocol, status, status_text = start_line.split(b" ", maxsplit=2)

        if protocol != b"HTTP/1.1":
            msg = "Only HTTP/1.1 is supported"
            raise HttpError(msg)

        return ResponseOptions(status=int(status), status_text=status_text.decode("ascii"), headers=headers)

    @staticmethod
    def _parse_headers(lines: List[bytes]) -> Dict[str, str]:
        headers = {}
        for line in lines:
            key, value = line.split(b":", maxsplit=1)
            headers[key.strip().decode("ascii")] = value.strip().decode("ascii")

        return headers


class ContentLengthBodyParser:
    def __init__(self, headers):
        self.headers = headers
        self.body = b""

    def push(self, data: bytes) -> None:
        self.body += data

    def finished(self) -> bool:
        if "Content-Length" in self.headers:
            if len(self.body) >= int(self.headers["Content-Length"]):
                return True
        return False
