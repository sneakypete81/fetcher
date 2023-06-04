import asyncio
import logging
from typing import Union

from fetcher.http import Request, Response, parse_response

logger = logging.getLogger("fetch")


async def fetch(resource: str) -> Response:
    request = Request(resource)
    reader, writer = await asyncio.open_connection(request.hostname, request.port)
    trace("*", f"Connected to {request.hostname} port {request.port}")

    trace(">", request.data)
    writer.write(request.data)
    writer.write_eof()
    data = await reader.read()
    trace("<", data)

    return parse_response(data)


def trace(prefix: str, data: Union[str, bytes]):
    if isinstance(data, bytes):
        data = data.decode("ascii")

    for line in data.splitlines():
        logger.info(f"{prefix} {line}")
