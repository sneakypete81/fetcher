import asyncio

from fetcher.http import Request, Response, parse_response
from fetcher.trace import trace


async def fetch(resource: str) -> Response:
    request = Request(resource)
    reader, writer = await asyncio.open_connection(request.hostname, request.port)
    trace("*", f"Connected to {request.hostname} port {request.port}")

    trace(">", request.data)
    writer.write(request.data)
    writer.write_eof()
    data = await reader.read()

    return parse_response(data)
