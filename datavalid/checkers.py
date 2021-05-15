import datetime

import pandas as pd

from .condition import Condition
from .date import DateParser
from .exceptions import BadConfigError


class UniqueChecker(object):
    def __init__(self, columns: str or list[str]) -> None:
        if type(columns) is str:
            self._columns = [columns]
        elif type(columns) is list:
            self._columns = columns
        else:
            raise BadConfigError(
                [], 'should be a column name or a list of column names'
            )

    def check(self, df: pd.DataFrame) -> bool:
        succeed = not df.duplicated(subset=self._columns).any()
        if not succeed:
            self.err_msg = 'Table contains duplicates'
            self.df = df[df.duplicated(subset=self._columns, keep=False)]
        return succeed


class EmptyChecker(object):
    def __init__(self, **kwargs) -> None:
        self._condition = Condition(**kwargs)

    def check(self, df: pd.DataFrame) -> bool:
        succeed = not self._condition.bool_index(df).any()
        if not succeed:
            df = self._condition.apply(df)
            self.err_msg = 'There are %d such rows' % df.shape[0]
            self.df = df
        return succeed


class NoConsecutiveDateChecker(object):
    def __init__(self, date_from: dict or None = None) -> None:
        if date_from is None:
            raise BadConfigError([], 'should contain key "date_from"')
        if type(date_from) is not dict:
            raise BadConfigError([], '"date_from" should be a dict')
        try:
            self._date_parser = DateParser(**date_from)
        except BadConfigError as e:
            raise BadConfigError(['date_from']+e.path, e.msg)
        except TypeError as e:
            raise BadConfigError(['date_from'], str(e))

    def check(self, df: pd.DataFrame) -> bool:
        date_series = self._date_parser.parse(df)
        prev_date = None
        prev_ind = None
        succeed = True
        for ind, date in date_series.sort_values().items():
            if prev_date is None:
                prev_date = date
                prev_ind = ind
            elif prev_date == date - datetime.timedelta(days=1):
                succeed = False
                break
        if not succeed:
            df = df.loc[[prev_ind, ind]]
            self.err_msg = 'Consecutive dates detected'
            self.df = df
        return succeed


class NoMoreThanOnceAMonthChecker(object):
    def __init__(self, date_from: dict or None = None) -> None:
        if date_from is None:
            raise BadConfigError([], 'should contain key "date_from"')
        if type(date_from) is not dict:
            raise BadConfigError([], '"date_from" should be a dict')
        try:
            self._date_parser = DateParser(**date_from)
        except BadConfigError as e:
            raise BadConfigError(['date_from']+e.path, e.msg)
        except TypeError as e:
            raise BadConfigError(['date_from'], str(e))

    def check(self, df: pd.DataFrame) -> bool:
        date_series = self._date_parser.parse(df)
        df = df.copy(True)
        year_month = date_series.dt.strftime("%b, %Y")
        succeed = True
        for val in year_month.unique():
            subdf = df.loc[year_month == val]
            if subdf.shape[0] > 1:
                succeed = False
                self.err_msg = 'More than 1 row detected in the month %s' % val
                self.df = subdf
                break
        return succeed
