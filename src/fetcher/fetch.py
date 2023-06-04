import asyncio

from fetcher.http import Request


async def fetch(resource: str) -> None:
    request = Request(resource)
    reader, writer = await asyncio.open_connection(request.hostname, request.port)

    writer.write(request.data)
    await reader.read()
