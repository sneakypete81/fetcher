import asyncio

from fetcher.http import HttpRequest, Response, ResponseParser
from fetcher.trace import trace

FRAGMENT_SIZE = 1024


async def fetch(resource: str) -> Response:
    http_request = HttpRequest(resource)
    reader, writer = await asyncio.open_connection(http_request.hostname, http_request.port)
    trace("*", f"Connected to {http_request.hostname} port {http_request.port}")

    trace(">", http_request.data)
    writer.write(http_request.data)

    parser = ResponseParser()
    while True:
        fragment = await reader.read(FRAGMENT_SIZE)
        parser.push_fragment(fragment)
        if parser.finished or reader.at_eof():
            return parser.response()
