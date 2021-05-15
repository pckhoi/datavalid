import pandas as pd

from .checkers import NoMoreThanOnceAMonthChecker, UniqueChecker, EmptyChecker, NoConsecutiveDateChecker
from .filter import Filter


class Task(object):
    def __init__(
        self, name: str, where: dict or None = None, group_by: str or None = None,
        unique: str or list[str] or None = None, empty: dict or None = None,
        no_consecutive_date: dict or None = None, no_more_than_once_a_month: dict or None = None
    ) -> None:
        self.name = name
        self._filter = Filter(where, group_by)
        if unique is not None:
            self._checker = UniqueChecker(unique)
        if empty is not None:
            self._checker = EmptyChecker(**empty)
        if no_consecutive_date is not None:
            self._checker = NoConsecutiveDateChecker(**no_consecutive_date)
        if no_more_than_once_a_month is not None:
            self._checker = NoMoreThanOnceAMonthChecker(
                **no_more_than_once_a_month)

    def run(self, df: pd.DataFrame) -> bool:
        for sub_df in self._filter.filter(df):
            succeed = self._checker.check(sub_df)
            if not succeed:
                return False
        return True

    @property
    def err_msg(self) -> str:
        return self._checker.err_msg
