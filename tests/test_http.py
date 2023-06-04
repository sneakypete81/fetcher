from hamcrest import assert_that, equal_to

from fetcher import http


def test_simple_http_request():
    request = http.Request("http://www.example.com")

    assert_that(request.data, equal_to(b"GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n"))


def test_http_request_with_no_scheme():
    request = http.Request("www.example.com")

    assert_that(request.data, equal_to(b"GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n"))


def test_http_request_with_a_path():
    request = http.Request("www.example.com/path/to/file")

    assert_that(request.data, equal_to(b"GET /path/to/file HTTP/1.1\r\nHost: www.example.com\r\n\r\n"))
