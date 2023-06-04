import asyncio

from fetcher.http import Request, Response, parse_response


async def fetch(resource: str) -> Response:
    request = Request(resource)
    reader, writer = await asyncio.open_connection(request.hostname, request.port)

    writer.write(request.data)
    data = await reader.read()

    return parse_response(data)
