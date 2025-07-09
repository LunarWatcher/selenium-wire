from .e2e_utils import *

from seleniumwire import SeleniumWireOptions, Chrome
from seleniumwire.request import Response

import json
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
    res = driver.last_request.response
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
    assert driver.requests[-1].response.headers.get("content-encoding") \
        == "br"
    _decompress(driver.requests[-1].response)

def test_decompress_with_deflate(driver: Chrome, httpbin: Httpbin):
    driver.get(f"{httpbin}/deflate")
    assert driver.requests[-1].response.headers.get("content-encoding") \
        == "deflate"
    _decompress(driver.requests[-1].response)

def test_decompress_with_gzip(driver: Chrome, httpbin: Httpbin):
    driver.get(f"{httpbin}/gzip")
    assert driver.requests[-1].response.headers.get("content-encoding") \
        == "gzip"
    _decompress(driver.requests[-1].response)
