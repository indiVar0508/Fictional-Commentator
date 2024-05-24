"""
A basic template to define what should be basic level of methods that is need to fetch Data for a sport
TODO: currently only focus on cricket future we can expand on it.
"""

import urllib.request
import json
from ..exceptions import ScoreFetchAPIError
from ..util import retry_with_timeout


@retry_with_timeout
def request_open(req):
    try:
        with urllib.request.urlopen(req) as resp:
            # Read the response
            data = resp.read()
            # Decode the data to a string
            return data.decode("utf-8")
    except Exception as e:
        raise ScoreFetchAPIError(e.__str__())


class BaseFetcher:
    @classmethod
    def _get_request_object(
        cls, url, headers: dict = {}, data: dict = {}
    ) -> urllib.request.Request:
        return urllib.request.Request(url, headers=headers, data=data)

    @classmethod
    def get_data(cls, url: str, headers: dict = {}, data: dict = None) -> str:
        return request_open(cls._get_request_object(url, headers, data))

    @classmethod
    def get_json_data(cls, url: str, headers: dict = {}, data: dict = None) -> dict:
        data = cls.get_data(url, headers, data)
        return json.loads(data)
