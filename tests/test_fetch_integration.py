import asyncio

import pytest

import fetcher


class FakeServer:
    def __init__(self):
        self.data = b""
        self._server = None

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._on_connect, host="localhost")

    def port(self) -> int:
        return self._server.sockets[0].getsockname()[1]

    async def _on_connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        await reader.read(1024)
        writer.write(self.data)
        writer.close()


@pytest.fixture(scope="module")
def server():
    return FakeServer()


@pytest.mark.asyncio
async def test_fetch_http_url(server: FakeServer):
    server.data = b"Hello"
    await server.start()

    await fetcher.fetch(f"http://localhost:{server.port()}")
