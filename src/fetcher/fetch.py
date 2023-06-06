import asyncio

from fetcher.http import Request, Response, ResponseParser
from fetcher.trace import trace

FRAGMENT_SIZE = 1024


async def fetch(resource: str) -> Response:
    request = Request(resource)
    reader, writer = await asyncio.open_connection(request.hostname, request.port)
    trace("*", f"Connected to {request.hostname} port {request.port}")

    trace(">", request.data)
    writer.write(request.data)

    parser = ResponseParser()
    while True:
        fragment = await reader.read(FRAGMENT_SIZE)
        parser.push_fragment(fragment)
        if parser.finished or reader.at_eof():
            return parser.response()
