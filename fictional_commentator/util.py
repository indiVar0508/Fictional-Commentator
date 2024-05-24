"""
Re-Usable utility methods
"""

import time
from .exceptions import FetchAPIError


def retry_with_timeout(func):
    def inner_retry_with_timeout(*args, **kwargs):
        tries = 5
        while tries > 0:
            try:
                return func(*args, **kwargs)
            except FetchAPIError as fe:
                # Wait 10s
                print(f"{func} failed, waiting for 10s", fe.__str__())
                time.sleep(10)
                tries -= 1

    return inner_retry_with_timeout
