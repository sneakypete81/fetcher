import asyncio

import pytest

import fetcher


class TestServer:
    async def start(self) -> None:
        self._server = await asyncio.start_server(self._on_connect, host="localhost")

    def port(self) -> int:
        return self._server.sockets[0].getsockname()[1]

    async def _on_connect(self, reader, writer):
        data = await reader.read(100)
        writer.write(data)
        writer.close()


@pytest.fixture(scope="module")
def server():
    return TestServer()


@pytest.mark.asyncio
async def test_fetch_http_url(server):
    await server.start()

    await fetcher.fetch(f"http://localhost:{server.port()}")
