import pytest
from contextlib import contextmanager
from seleniumwire import webdriver
from tests import utils as testutils
from tests.httpbin_server import Httpbin
import shutil
import os
from seleniumwire.options import SeleniumWireOptions
from selenium.webdriver.chrome.service import Service
from pathlib import Path

@pytest.fixture(scope="module")
def httpbin():
    # This module scoped Httpbin fixture uses HTTPS
    with create_httpbin() as httpbin:
        yield httpbin


@contextmanager
def create_httpbin(port=8085, use_https=True):
    httpbin = Httpbin(port, use_https)
    try:
        yield httpbin
    finally:
        httpbin.shutdown()


@pytest.fixture(scope="module")
def httpproxy():
    with create_httpproxy() as proxy:
        yield proxy


@contextmanager
def create_httpproxy(port=8086, mode="http", auth=""):
    httpproxy = testutils.Proxy(port, mode, auth)
    try:
        yield httpproxy
    finally:
        httpproxy.shutdown()


@pytest.fixture
def driver_path():
    return os.getenv("CHROMEDRIVER_PATH") or ""


@pytest.fixture
def chrome_options():
    options = webdriver.ChromeOptions()
    options.binary_location = testutils.get_chromium_path()
    options.add_argument("--headless=new")
    return options


@pytest.fixture
def driver(driver_path, chrome_options):
    with create_driver(driver_path, chrome_options) as driver:
        yield driver


@contextmanager
def create_driver(
    driver_path,
    chrome_options,
    seleniumwire_options=SeleniumWireOptions(),
):
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=seleniumwire_options)
    filter_chrome_requests(driver)
    try:
        yield driver
    finally:
        driver.quit()


def teardown_function():
    try:
        (Path(__file__).parent / Path("linux", "chrome_debug.log")).unlink()
    except FileNotFoundError:
        pass

    try:
        (Path(__file__).parent / Path("html.html")).unlink()
    except FileNotFoundError:
        pass

    shutil.rmtree(Path(__file__).parent / Path("linux", "locales"), ignore_errors=True)

    shutil.rmtree(Path(__file__).parent / "chrome_tmp", ignore_errors=True)


def filter_chrome_requests(driver: webdriver.Chrome):
    del driver.requests
    driver.exclude_urls += [r".*google\.com.*"]
