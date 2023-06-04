from hamcrest import assert_that, equal_to

from fetcher import http


class TestRequest:
    def test_simple(self):
        request = http.Request("http://www.example.com")

        assert_that(request.data, equal_to(b"GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n"))

    def test_with_no_scheme(self):
        request = http.Request("www.example.com")

        assert_that(request.data, equal_to(b"GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n"))

    def test_with_a_path(self):
        request = http.Request("www.example.com/path/to/file")

        assert_that(request.data, equal_to(b"GET /path/to/file HTTP/1.1\r\nHost: www.example.com\r\n\r\n"))

    def test_with_a_port(self):
        request = http.Request("www.example.com:1234")

        assert_that(request.port, equal_to(1234))

    def test_with_no_port_defaults_to_port_80(self):
        request = http.Request("www.example.com")

        assert_that(request.port, equal_to(80))


class TestResponse:
    def test_ok_status_code(self):
        response = http.parse_response(b"HTTP/1.1 200 OK\r\n\r\n")

        assert_that(response.ok)
        assert_that(response.status, equal_to(200))
        assert_that(response.status_text, equal_to("OK"))

    def test_error_status_code(self):
        response = http.parse_response(b"HTTP/1.1 404 Not Found\r\n\r\n")

        assert_that(not response.ok)
        assert_that(response.status, equal_to(404))
        assert_that(response.status_text, equal_to("Not Found"))
