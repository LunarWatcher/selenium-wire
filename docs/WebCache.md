# WebCache

```python3
import seleniumwire.helpers.cache
```

Utility class for caching web content, primarily supporting content required for the webdriver to run that only needs to be cached once before use, in applications where one or multiple webdriver instances are spun up semi-regularly. 

## Use-case

The `WebCache` class is a utility class for caching web content. This is primarily intended for stuff like setup, where the downloaded content is stable over a period of time. A practical application of this is when using uBlock Origin - yes, you _can_ redownload the filter lists every time you set up a driver, but if you have a long-running application, you could also cache these results, both to help with performance, and to avoid hitting GitHub or various other sites with requests regularly[^1].

One thing to note is that the WebCache does not cache anything on disk; the content is cached in memory, because it's assumed there isn't huge quantities of data involved. The cache is build on the assumption that

1. The content you're caching is well-defined in scope, but not necessarily in exact content. In the case of uBlock filter lists, for example, the content is known, but the exact sources may vary by uBlock version
2. The content you're caching isn't intended for use in scraping. The easiest way, depending on your use-case, is either to use seleniumwire in disk mode, or manually writing the responses to disk. 
3. The status code is 2xx or 3xx, and 200 is always accepted; the status code will be flattened to 200 after the caching process
4. The content you're caching has a well-defined time slot during execution. If the content you want to cache can appear at any time, you'll want to write your own request interceptor. If the content you want to cache is loaded during a specific period of time where you want the cache enabled

### Caveats

If you use a custom request and/or response interceptor, you must set it manually after using the cache. The cache uses both request and response interceptors to provide functionality, so anything you set before using the cache will be cleared.

## Example use

```python3
# The cache object is reused globally. Note that it is not thread-safe,
# so if you need multithreading, you need to handle that yourself somehow
cache = WebCache()

# This is some generic example of a function that creates and uses a webdriver.
# You can also use it on a single-instance webdriver if that works better
# with your setup.
def run_webdriver(cache: WebCache):
    driver = TODO()
    # intercept_with returns a context manager that's used for 
    with cache.intercept_with(driver):
        # Do things that create requests you want to cache
        # If you want things excluded from the cache, the URLs need to be
        # excluded from seleniumwire outright. See the README
        driver.get("https://example.com/some-path-to-cache")

def on_event():
    run_webdriver(cache)
```

You _can_ also do cache manipulation should you need to, but this is strongly discouraged unless you do very basic changes. If you need to do extensive manipulation, you should write your own interceptors instead. If you want to manipulate the cache anyway, using the `run_webdriver` function from the example, the cache is available through `cache.cache`. The underlying cache object is a `dict[str, CachedResponse]`, where `CachedResponse` is a class that currently takes a response (byte object) and a mimetype (str).

[^1]: Another point, though I have no clue how much it matters, reducing traffic to services that may be covered by Cloudflare could help reduce the chance Cloudflare smacks your IP into oblivion.
