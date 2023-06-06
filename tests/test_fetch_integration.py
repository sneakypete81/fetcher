import asyncio

import pytest
from hamcrest import assert_that, equal_to

import fetcher


class FakeServer:
    MAX_READ_LENGTH = 1024

    def __init__(self):
        self.request_data = b""
        self.response_data = b""
        self._server = None

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._on_connect, host="localhost")

    def port(self) -> int:
        return self._server.sockets[0].getsockname()[1]

    async def _on_connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.request_data = await reader.read(self.MAX_READ_LENGTH)
        writer.write(self.response_data)


@pytest.fixture(scope="module")
def server():
    return FakeServer()


@pytest.mark.asyncio
async def test_fetch_http_url_with_content_length(server: FakeServer):
    server.response_data = b"HTTP/1.1 200 OK\r\nContent-Length:4\r\n\r\nBody"
    await server.start()

    response = await fetcher.fetch(f"http://localhost:{server.port()}/test/index.html")

    assert_that(
        server.request_data,
        equal_to(
            b"GET /test/index.html HTTP/1.1\r\nHost: localhost\r\n\r\n",
        ),
    )
    assert_that(response.status_text, equal_to("OK"))
    assert_that(response.status, equal_to(200))
    assert_that(response.ok)
    assert_that(response.body, equal_to(b"Body"))


@pytest.mark.asyncio
async def test_fetch_http_url_with_chunked_transfer_encoding(server: FakeServer):
    server.response_data = b"HTTP/1.1 200 OK\r\nTransfer-Encoding:chunked\r\n\r\n4\r\nBody\r\n0\r\n\r\n"
    await server.start()

    response = await fetcher.fetch(f"http://localhost:{server.port()}/test/index.html")

    assert_that(
        server.request_data,
        equal_to(
            b"GET /test/index.html HTTP/1.1\r\nHost: localhost\r\n\r\n",
        ),
    )
    assert_that(response.status_text, equal_to("OK"))
    assert_that(response.status, equal_to(200))
    assert_that(response.ok)
    assert_that(response.body, equal_to(b"Body"))
