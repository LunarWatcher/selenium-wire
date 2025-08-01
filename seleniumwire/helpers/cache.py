from http import HTTPStatus
from seleniumwire.inspect import InspectRequestsMixin

from dataclasses import dataclass
from contextlib import contextmanager

from seleniumwire.request import Request, Response

@dataclass
class CachedResponse:
    response: bytes
    mime: str

class WebCache:
    """
    Utility class for storing an arbitrary web cache. This is primarily used to
    override the uBlock filter lists to prevent them being fetched from remote
    every time a webdriver is started.

    This class is not thread-safe, and should not be called from multiple
    threads without sufficient safeguards.
    """
    def __init__(self, auto_clear: bool = False):
        """
        :param auto_clear       Whether or not to automatically delete
                                driver.requests when the `with` scope is exited 
        """
        self.cache: dict[str, CachedResponse] = {}
        self.auto_clear = auto_clear

    def get_cache_or_null(self, url):
        if url not in self.cache:
            return None
        return self.cache[url]

    def set_cache(self, url, response, mime):
        self.cache[url] = CachedResponse(
            response,
            mime
        )

    def intercept_with(self, driver):
        assert isinstance(driver, InspectRequestsMixin), \
            "The WebCache needs a seleniumwire webdriver"
        def request_interceptor(request: Request):
            if request.url in self.cache:
                data = self.cache[request.url]
                return request.create_response(
                    HTTPStatus.OK,
                    headers = {
                        "Content-Type": data.mime
                    },
                    body=data.response
                )

        def response_interceptor(request: Request, response: Response):
            if request.url not in self.cache:
                self.cache[request.url] = CachedResponse(
                    # The body has to be decompressed, or another header has to
                    # be stored, and I don't want to
                    response.decompress_body(),
                    # I would assume the content type is always present
                    response.headers.get("content-type", "text/plain")
                )

        @contextmanager
        def _internal():
            driver.request_interceptor = request_interceptor
            driver.response_interceptor = response_interceptor
            yield self
            del driver.request_interceptor
            del driver.response_interceptor
            if self.auto_clear:
                del driver.requests

        return _internal()

    # def __enter__(self):
        # assert self.driver is not None, \
            # "Call intercept_with first"

    # def __exit__(self, exc_type, exc_value, traceback):
        # # Probably an assertion error, or bad end-user code
        # if self.driver is None:
            # return

        # if self.auto_clear:
            # del self.driver.requests
        # self.driver = None
