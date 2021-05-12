import pandas as pd

from .checks import UniqueCheck, EmptyCheck, NoConsecutiveDateCheck
from .filter import Filter


class Task(object):
    def __init__(
            self, name: str, unique: list = None, empty: dict = None, no_consecutive_date: dict = None,
            where: dict = None, group_by: dict or str = None) -> None:
        self.name = name
        if unique is not None:
            self._check = UniqueCheck(unique)
        elif empty is not None:
            self._check = EmptyCheck(empty)
        elif no_consecutive_date is not None:
            self._check = NoConsecutiveDateCheck(no_consecutive_date)
        self._filter = Filter(where, group_by)

    def run(self, df: pd.DataFrame) -> bool:
        for sub_df in self._filter.filter(df):
            succeed = self._check.check(sub_df)
            if not succeed:
                return False
        return True

    def print_error(self) -> None:
        self._check.print_error()
