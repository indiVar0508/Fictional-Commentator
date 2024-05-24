"""
Basic Expection that can occur
"""


class BaseException(Exception):
    pass


class FetchAPIError(BaseException):
    pass


class ScoreFetchAPIError(FetchAPIError):
    # TODO: Add some string
    pass
