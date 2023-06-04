import asyncio

import pytest
from hamcrest import assert_that, equal_to

import fetcher


class FakeServer:
    def __init__(self):
        self.request_data = b""
        self.response_data = b""
        self._server = None

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._on_connect, host="localhost")

    def port(self) -> int:
        return self._server.sockets[0].getsockname()[1]

    async def _on_connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.request_data = await reader.read()
        writer.write(self.response_data)
        writer.close()


@pytest.fixture(scope="module")
def server():
    return FakeServer()


@pytest.mark.asyncio
async def test_fetch_http_url(server: FakeServer):
    server.response_data = b"HTTP/1.1 200 OK\r\n\r\n"
    await server.start()

    response = await fetcher.fetch(f"http://localhost:{server.port()}/test/index.html")

    assert_that(
        server.request_data,
        equal_to(
            b"GET /test/index.html HTTP/1.1\r\nHost: localhost\r\n\r\n",
        ),
    )
    assert_that(response.status_text, equal_to("OK"))
    assert_that(response.ok)
