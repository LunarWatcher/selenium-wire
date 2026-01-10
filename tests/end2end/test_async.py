import asyncio
import time

from seleniumwire.webdriver import Chrome, SeleniumWireOptions
from selenium.webdriver import ChromeService as Service
from selenium.webdriver.common.by import By
from tests.conftest import filter_chrome_requests
from pytest import fail, skip

def test_async_does_not_throw(
    driver_path,
    chrome_options,
    httpbin
):
    # return skip(
    #     reason=(
    #         "quit() in an async calling function results in the quitting "
    #         "thread blocking for up to a minute"
    #     )
    # )
    async def async_func():
        driver = None
        try:
            driver = Chrome(
                service=Service(executable_path=driver_path),
                options=chrome_options
            )
            filter_chrome_requests(driver)

            # Exact same as test_end2end::test_capture_requests {{{
            driver.get(f"{httpbin}/html")
            driver.find_element(By.TAG_NAME, "html")

            driver.wait_for_request(".*favicon\\.ico.*")
            assert driver.requests
            # Page request + automatic favicon request
            assert len(driver.requests) == 2
            for request in driver.requests:
                assert request is not None, request
            del driver.requests
            assert len(driver.requests) == 0
            # }}}
        finally:
            assert driver is not None
            driver.quit()
    start = time.monotonic()
    asyncio.run(async_func())
    end = time.monotonic()

    assert end - start < 5
