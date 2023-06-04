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


class TestResponse:
    def test_ok_status_code(self):
        response = http.parse_response(b"HTTP/1.1 200 OK")

        assert_that(response.ok)
        assert_that(response.status_text, equal_to("OK"))

    def test_error_status_code(self):
        response = http.parse_response(b"HTTP/1.1 404 Not Found")

        assert_that(not response.ok)
        assert_that(response.status_text, equal_to("Not Found"))
