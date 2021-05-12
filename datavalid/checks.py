from .condition import Condition
from .date import DateParser


class UniqueCheck(object):
    def __init__(self, columns: list) -> None:
        self._columns = columns


class EmptyCheck(object):
    def __init__(self, **kwargs) -> None:
        self._condition = Condition(**kwargs)


class NoConsecutiveDateCheck(object):
    def __init__(self, date_from: dict) -> None:
        self._date_parser = DateParser(**date_from)
