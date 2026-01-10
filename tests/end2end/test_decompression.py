from seleniumwire import SeleniumWireOptions, Chrome
from seleniumwire.request import Response
from tests.httpbin_server import Httpbin

import json
import time
import pytest

def _decompress(response):
    assert isinstance(response, Response), "Didn't receive a response. Misconfigured test"
    body = response.body

    assert body is not None
    assert len(body) > 0
    with pytest.raises((json.decoder.JSONDecodeError, UnicodeDecodeError)):
        json.loads(body)
    decoded_body = response.decompress_body()
    assert decoded_body != body

    json.loads(decoded_body)

def test_decompress_with_nothing(driver: Chrome, httpbin: Httpbin):
    driver.get(f"{httpbin}/json")
    time.sleep(1)
    res = driver.requests[0].response
    assert res.status_code == 200, res.body

    body = res.body
    assert body is not None
    assert len(body) > 0
    assert json.loads(body) is not None
    assert json.loads(res.decompress_body()) is not None

# Not yet supported by httpbin
# def test_decompress_with_zstd(driver: Chrome, httpbin: Httpbin):
    # driver.get(f"{httpbin}/zstd")
    # _decompress(driver.requests[-1].response)

def test_decompress_with_brotli(driver: Chrome, httpbin: Httpbin):
    driver.get(f"{httpbin}/brotli")
    driver.wait_for_request("/brotli")
    res = driver.requests[0].response
    assert res.status_code == 200, res.body
    assert res.headers.get("content-encoding") \
        == "br"
    _decompress(res)

def test_decompress_with_deflate(driver: Chrome, httpbin: Httpbin):
    driver.get(f"{httpbin}/deflate")
    driver.wait_for_request("/deflate")
    res = driver.requests[0].response
    assert res.status_code == 200, res.body
    assert res.headers.get("content-encoding") \
        == "deflate"
    _decompress(res)

def test_decompress_with_gzip(driver: Chrome, httpbin: Httpbin):
    driver.get(f"{httpbin}/gzip")
    driver.wait_for_request("/gzip")
    res = driver.requests[0].response
    assert res.status_code == 200, res.body
    assert res.headers.get("content-encoding") \
        == "gzip"
    _decompress(res)
