import datetime

import pandas as pd

from .condition import Condition
from .date import DateParser
from .exceptions import BadConfigError


class UniqueChecker(object):
    """Checks whether a table is unique per given columns

    Attributes:
        err_msg (str): error message, available if check() returns False
        df (pd.DataFrame): offending rows, available if check() returns False
    """

    def __init__(self, columns: str or list[str]) -> None:
        """Creates new instance of UniqueChecker

        Args:
            columns (str or list[str]): list of column names to check for uniqueness

        Raises:
            BadConfigError: There's a problem with passed-in arguments

        Returns:
            no value
        """
        if type(columns) is str:
            self._columns = [columns]
        elif type(columns) is list:
            self._columns = columns
        else:
            raise BadConfigError(
                [], 'should be a column name or a list of column names'
            )

    def check(self, df: pd.DataFrame) -> bool:
        """Returns whether table pass the check

        Args:
            df (pd.DataFrame): data to perform check on

        Returns:
            True or False depending on whether data pass the check.
        """
        succeed = not df.duplicated(subset=self._columns).any()
        if not succeed:
            self.err_msg = 'Table contains duplicates'
            self.df = df[df.duplicated(subset=self._columns, keep=False)]
        return succeed


class EmptyChecker(object):
    """Checks whether a table have no row with specified condition

    Attributes:
        err_msg (str): error message, available if check() returns False
        df (pd.DataFrame): offending rows, available if check() returns False
    """

    def __init__(self, **kwargs) -> None:
        """Creates new instance of EmptyChecker

        Args:
            Same arguments as those passed to Condition()

        Returns:
            no value
        """
        self._condition = Condition(**kwargs)

    def check(self, df: pd.DataFrame) -> bool:
        """Returns whether table pass the check

        Args:
            df (pd.DataFrame): data to perform check on

        Returns:
            True or False depending on whether data pass the check.
        """
        succeed = not self._condition.bool_index(df).any()
        if not succeed:
            df = self._condition.apply(df)
            self.err_msg = 'There are %d such rows' % df.shape[0]
            self.df = df
        return succeed


class NoConsecutiveDateChecker(object):
    """Checks that a table contains no consecutive date

    Attributes:
        err_msg (str): error message, available if check() returns False
        df (pd.DataFrame): offending rows, available if check() returns False
    """

    def __init__(self, date_from: dict or None = None) -> None:
        """Creates new instance of NoConsecutiveDateChecker

        Args:
            date_from (dict): arguments to pass to DateParser()

        Raises:
            BadConfigError: There's a problem with passed-in arguments

        Returns:
            no value
        """
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
        """Returns whether table pass the check

        Args:
            df (pd.DataFrame): data to perform check on

        Returns:
            True or False depending on whether data pass the check.
        """
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


class NoMoreThanOncePer30DaysChecker(object):
    """Checks that a table contains no 2 rows which is 30 days apart or less

    Attributes:
        err_msg (str): error message, available if check() returns False
        df (pd.DataFrame): offending rows, available if check() returns False
    """

    def __init__(self, date_from: dict or None = None) -> None:
        """Creates new instance of NoMoreThanOncePer30DaysChecker

        Args:
            date_from (dict): arguments to pass to DateParser()

        Raises:
            BadConfigError: There's a problem with passed-in arguments

        Returns:
            no value
        """
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
        """Returns whether table pass the check

        Args:
            df (pd.DataFrame): data to perform check on

        Returns:
            True or False depending on whether data pass the check.
        """
        df = df.copy(True)
        df.loc[:, 'datavalid_date'] = self._date_parser.parse(df)
        df = df.sort_values('datavalid_date')
        prev_date = None
        prev_idx = None
        indices = set()
        for idx, row in df.iterrows():
            if prev_date is not None and prev_date + datetime.timedelta(days=30) >= row.datavalid_date:
                indices.add(prev_idx)
                indices.add(idx)
            prev_date = row.datavalid_date
            prev_idx = idx
        if len(indices) > 0:
            self.err_msg = '%d rows detected occur too close together' % len(
                indices
            )
            self.df = df.loc[list(indices)].sort_values('datavalid_date')\
                .drop(columns=['datavalid_date'])
            return False
        return True
