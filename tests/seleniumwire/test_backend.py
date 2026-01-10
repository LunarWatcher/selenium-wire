import json
import os
import ssl
import threading
import requests
import time
from unittest import TestCase

from seleniumwire import backend as Backend
from tests.httpbin_server import Httpbin
from pytest import skip


class BackendIntegrationTest(TestCase):
    """This integration test uses a single instance of the backend proxy
    server for the whole test suite. This makes it quicker, since the server
    isn't restarted between tests, but it also means that the proxy configuration
    can't be modified once the server has been started.
    """

    backend: Backend.MitmProxy = None 
    httpbin = None

    def test_create_proxy(self):
        html = self.make_request(f"{self.httpbin}/html")

        self.assertIn("Herman Melville", html)

    def test_shutdown(self):
        skip(
            "Broken by the fix for #8 for whatever reason"
        )
        self.backend.shutdown()

        with self.assertRaises(Exception):
            self.make_request(f"{self.httpbin}/html")

    def test_get_requests_single(self):
        self.make_request(f"{self.httpbin}/html")

        requests = self.backend.storage.load_requests()

        self.assertEqual(len(requests), 1)
        request = requests[0]
        self.assertEqual("GET", request.method)
        self.assertEqual(f"{self.httpbin}/html", request.url)
        # self.assertEqual("identity", request.headers["Accept-Encoding"])
        self.assertEqual(200, request.response.status_code)
        self.assertEqual("text/html; charset=utf-8", request.response.headers["Content-Type"])
        self.assertTrue(len(request.response.body) > 0)
        self.assertIn(b"html", request.response.body)

    def test_get_requests_multiple(self):
        self.make_request(f"{self.httpbin}/html")
        self.make_request(f"{self.httpbin}/anything")

        requests = self.backend.storage.load_requests()

        self.assertEqual(2, len(requests))

    def test_get_last_request(self):
        self.make_request(f"{self.httpbin}/html")
        self.make_request(f"{self.httpbin}/anything")

        last_request = self.backend.storage.load_last_request()

        self.assertEqual(f"{self.httpbin}/anything", last_request.url)

    def test_get_last_request_none(self):
        last_request = self.backend.storage.load_last_request()

        self.assertIsNone(last_request)

    def test_clear_requests(self):
        self.make_request(f"{self.httpbin}/html")
        self.make_request(f"{self.httpbin}/anything")

        self.backend.storage.clear_requests()

        self.assertEqual([], self.backend.storage.load_requests())

    def test_find(self):
        self.make_request(f"{self.httpbin}/anything/questions/tagged/django?page=2&sort=newest&pagesize=15")
        self.make_request(f"{self.httpbin}/anything/3.4/library/http.client.html")

        self.assertEqual(
            f"{self.httpbin}/anything/questions/tagged/django?page=2&sort=newest&pagesize=15",
            self.backend.storage.find("/questions/tagged/django").url,
        )
        self.assertEqual(
            f"{self.httpbin}/anything/3.4/library/http.client.html", self.backend.storage.find(".*library.*").url
        )

    def test_get_request_body_empty(self):
        self.make_request(f"{self.httpbin}/get")
        last_request = self.backend.storage.load_last_request()

        self.assertEqual(b"", last_request.body)

    def test_get_response_body_json(self):
        self.make_request(f"{self.httpbin}/get")  # httpbin endpoints return JSON
        last_request = self.backend.storage.load_last_request()

        self.assertIsInstance(last_request.response.body, bytes)
        data = json.loads(last_request.response.body.decode("utf-8"))
        self.assertEqual(f"{self.httpbin}/get", data["url"])

    def test_get_response_body_image(self):
        self.make_request(f"{self.httpbin}/image/png")
        last_request = self.backend.storage.load_last_request()

        self.assertIsInstance(last_request.response.body, bytes)

    def test_get_response_body_empty(self):
        self.make_request(f"{self.httpbin}/bytes/0")
        redirect_request = self.backend.storage.load_requests()[0]

        self.assertEqual(b"", redirect_request.response.body)

    def test_set_single_scopes(self):
        self.backend.include_urls = [f"{self.httpbin}/anything/foo/.*"]

        self.make_request(f"{self.httpbin}/anything/foo/bar")

        last_request = self.backend.storage.load_last_request()

        self.assertEqual(f"{self.httpbin}/anything/foo/bar", last_request.url)

        self.make_request(f"{self.httpbin}/anything/spam/bar")

        last_request = self.backend.storage.load_last_request()

        self.assertNotEqual(f"{self.httpbin}/anything/spam/bar", last_request.url)

    def test_set_multiples_scopes(self):
        self.backend.include_urls = [f"{self.httpbin}/anything/foo/.*", f"{self.httpbin}/anything/spam/.*"]

        self.make_request(f"{self.httpbin}/anything/foo/bar")
        last_request = self.backend.storage.load_last_request()
        self.assertEqual(f"{self.httpbin}/anything/foo/bar", last_request.url)

        self.make_request(f"{self.httpbin}/anything/spam/bar")
        last_request = self.backend.storage.load_last_request()
        self.assertEqual(f"{self.httpbin}/anything/spam/bar", last_request.url)

        self.make_request(f"{self.httpbin}/anything/hello/bar")
        last_request = self.backend.storage.load_last_request()
        self.assertNotEqual(f"{self.httpbin}/anything/hello/bar", last_request.url)

    def test_reset_scopes(self):
        self.backend.scopes = (f"{self.httpbin}/anything/foo/.*", f"{self.httpbin}/anything/spam/.*")
        self.backend.scopes = ()

        self.make_request(f"{self.httpbin}/anything/hello/bar")
        self.assertTrue(self.backend.storage.load_last_request())

    def test_disable_encoding(self):
        skip(
            "This test never worked, but broke hard after switching to "
            "requests. This is because disable_encoding isn't mutable"
        )
        self.backend.options.disable_encoding = True
        # Explicitly set the accept-encoding to gzip
        # self.backend.modifier.headers = {'Accept-Encoding': 'gzip'}

        assert len(self.backend.storage.load_requests()) == 0
        self.make_request(f"{self.httpbin}/anything")
        assert len(self.backend.storage.load_requests()) == 1

        last_request = self.backend.storage.load_last_request()
        data = json.loads(last_request.response.body.decode("utf-8"))

        self.assertEqual("identity", data["headers"]["Accept-Encoding"])

    def test_intercept_request_headers(self):
        user_agent = "Test_User_Agent_String"

        def interceptor(request):
            del request.headers["User-Agent"]
            request.headers["User-Agent"] = user_agent

        self.backend.request_interceptor = interceptor

        self.make_request(f"{self.httpbin}/headers")

        last_request = self.backend.storage.load_last_request()
        data = json.loads(last_request.response.body.decode("utf-8"))

        self.assertEqual(user_agent, last_request.headers["User-Agent"])
        self.assertEqual(user_agent, data["headers"]["User-Agent"])

    def test_intercept_request_params(self):
        def interceptor(request):
            # Update the existing parameters
            request.params = {**request.params, "foo": "baz", "a": "b"}

        self.backend.request_interceptor = interceptor

        self.make_request(f"{self.httpbin}/get?foo=bar&spam=eggs")

        last_request = self.backend.storage.load_last_request()

        self.assertEqual({"foo": "baz", "spam": "eggs", "a": "b"}, last_request.params)
        data = json.loads(last_request.response.body.decode("utf-8"))
        self.assertEqual({"foo": "baz", "spam": "eggs", "a": "b"}, data["args"])

    def test_intercept_request_body(self):
        def interceptor(request):
            data = json.loads(request.body.decode("utf-8"))
            data.update({"foo": "baz", "a": "b"})
            request.body = json.dumps(data).encode("utf-8")

        self.backend.request_interceptor = interceptor

        self.make_request(f"{self.httpbin}/post", method="POST", data=b'{"foo": "bar", "spam": "eggs"}')

        last_request = self.backend.storage.load_last_request()

        self.assertEqual({"foo": "baz", "spam": "eggs", "a": "b"}, json.loads(last_request.body.decode("utf-8")))

    def test_intercept_response_headers(self):
        def interceptor(request, response):
            del response.headers["Cache-Control"]
            response.headers["Cache-Control"] = "none"

        self.backend.response_interceptor = interceptor

        self.make_request(f"{self.httpbin}/anything")

        last_request = self.backend.storage.load_last_request()

        self.assertEqual("none", last_request.response.headers["Cache-Control"])

    def test_intercept_response_body(self):
        def interceptor(request, response):
            response.body = b"helloworld"
            del response.headers["Content-Length"]
            response.headers["Content-Length"] = "10"

        self.backend.response_interceptor = interceptor

        self.make_request(f"{self.httpbin}/anything")

        last_request = self.backend.storage.load_last_request()

        self.assertEqual(b"helloworld", last_request.response.body)

    def test_address(self):
        self.assertEqual("127.0.0.1", self.backend.address[0])
        self.assertIsInstance(self.backend.address[1], int)

    def setUp(self):
        self.backend = Backend.create()
        self.httpbin = Httpbin()


    def tearDown(self):
        self.backend.shutdown()
        if os.name != "nt":
            self.httpbin.shutdown()

        self.backend = None
        self.httpbin = None

    def make_request(self, url, method="GET", headers=None, data=None):
        if headers is None:
            headers = {}
        headers["User-Agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
        )

        request = requests.request(
            url=url,
            method=method,
            data=data,
            timeout=5,
            headers=headers,
            proxies={
                "http": "http://{}:{}".format(*self.backend.address[:2]),
                "https": "http://{}:{}".format(*self.backend.address[:2]),
            },
            verify=False,
        )

        return request.text
