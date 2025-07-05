"""Top-level package for Selenium Wire."""

__author__ = "LunarWatcher"
import importlib.metadata
try:
    __version__ = importlib.metadata.version("undetected-geckodriver-lw")
except:
    __version__ = "<unknown>"

from mitmproxy.certs import Cert
from mitmproxy.http import Headers

from seleniumwire.exceptions import SeleniumWireException
from seleniumwire.options import ProxyConfig, SeleniumWireOptions
from seleniumwire.webdriver import Chrome, Edge, Firefox, Remote, Safari
__all__ = [
    "Cert",
    "Headers",
    "SeleniumWireException",
    "ProxyConfig",
    "SeleniumWireOptions",
    "Chrome",
    "Edge",
    "Firefox",
    "Remote",
    "Safari",
]
try:
    from seleniumwire.webdriver import UndetectedFirefox
    __all__.append("UndetectedFirefox")
except:
    pass
try:
    from seleniumwire.webdriver import UndetectedChrome
    __all__.append("UndetectedChrome")
except:
    pass

