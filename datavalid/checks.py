import datetime

import pandas as pd

from .condition import Condition
from .date import DateParser


class UniqueCheck(object):
    def __init__(self, columns: str or list[str]) -> None:
        if type(columns) is str:
            self._columns = [columns]
        else:
            self._columns = columns

    def check(self, df: pd.DataFrame) -> bool:
        return not df.duplicated(subset=self._columns).any()


class EmptyCheck(object):
    def __init__(self, **kwargs) -> None:
        self._condition = Condition(**kwargs)

    def check(self, df: pd.DataFrame) -> bool:
        return not self._condition.bool_index(df).any()


class NoConsecutiveDateCheck(object):
    def __init__(self, date_from: dict) -> None:
        self._date_parser = DateParser(**date_from)

    def check(self, df: pd.DataFrame) -> bool:
        date_series = self._date_parser.parse(df)
        prev_date = None
        for _, date in date_series.sort_values().items():
            if prev_date is None:
                prev_date = date
            elif prev_date == date - datetime.timedelta(days=1):
                return False
        return True
