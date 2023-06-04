import asyncio
from urllib.parse import urlparse


async def fetch(resource: str) -> None:
    url = urlparse(resource, scheme="http")
    reader, writer = await asyncio.open_connection(url.hostname, url.port)
    writer.write(b"Hello")
    data = await reader.read()
    if data != b"Hello":
        msg = f"Expected 'Hello', got {data!r}"
        raise Exception(msg)
