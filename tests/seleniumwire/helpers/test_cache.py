import pytest

from seleniumwire.helpers.cache import WebCache
from seleniumwire.webdriver import Chrome

@pytest.fixture
def cache():
    yield WebCache()

def test_interceptors(driver: Chrome, cache: WebCache):
    """
    Tests that the cache cleans up after itself
    """
    assert driver.request_interceptor is None
    assert driver.response_interceptor is None

    with cache.intercept_with(driver):
        assert driver.request_interceptor is not None
        assert driver.response_interceptor is not None

    assert driver.request_interceptor is None
    assert driver.response_interceptor is None

def test_basic_cache(driver: Chrome, cache: WebCache, httpbin):
    assert len(cache.cache) == 0

    driver.get(f"{httpbin}/html")
    # TODO: using wait_for_request more extensively throughout the test suite
    # should make several of the tests more reliable
    # For favicon in particular though, do beware of caching. Once the driver
    # identifies that the icon is a 404, it won't re-request it, probably
    # unless you set an option to disable caching. Not sure if that's a thing
    # off the top of my head
    driver.wait_for_request(".*favicon\\.ico.*")
    assert len([
        request for request in driver.requests
        if f"{httpbin}" in request.url
    ]) == 2
    assert len(cache.cache) == 0

    del driver.requests
    assert len(driver.requests) == 0

    with cache.intercept_with(driver):
        driver.get(f"{httpbin}/html")
        assert len(cache.cache) == len(driver.requests)

    pre = len(driver.requests)
    driver.get(f"{httpbin}/html")
    assert len(cache.cache) == len(driver.requests) - pre

    # Override the cache content. In practice, this should never happen, but
    # this is an easy way to make sure the returned content is _not_ from the
    # underlying server
    cache.cache[f"{httpbin}/html"].response = b"Trans rights"
    cache.cache[f"{httpbin}/html"].mime = "text/plain"

    del driver.requests
    with cache.intercept_with(driver):
        driver.get(f"{httpbin}/html")
        # Unnecessary, gets pyright to shut up about nullability
        assert driver.last_request is not None
        assert driver.last_request.response is not None

        assert driver.last_request.response.body == b"Trans rights"
        assert driver.last_request.response.headers["content-type"] \
            == "text/plain"
        assert driver.last_request.response.status_code == 200
        # Can't do a == here because browsers wrap raw content in a bunch of
        # stock HTML
        assert "Trans rights" in driver.page_source
