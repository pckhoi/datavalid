import pandas as pd

from .checkers import NoMoreThanOnceAMonthChecker, UniqueChecker, EmptyChecker, NoConsecutiveDateChecker
from .filter import Filter
from .exceptions import BadConfigError


class Task(object):
    def __init__(
        self, name: str or None = None, where: dict or None = None, group_by: str or None = None,
        unique: str or list[str] or None = None, empty: dict or None = None,
        no_consecutive_date: dict or None = None, no_more_than_once_a_month: dict or None = None
    ) -> None:
        if name is None:
            raise BadConfigError(
                [],
                'task must have a name specified with "name" key'
            )
        self.name = name
        self._filter = Filter(where, group_by)
        if unique is not None:
            try:
                self._checker = UniqueChecker(unique)
            except BadConfigError as e:
                raise BadConfigError(['unique']+e.path, e.msg)
            except TypeError as e:
                raise BadConfigError(['unique'], str(e))
        elif empty is not None:
            try:
                self._checker = EmptyChecker(**empty)
            except BadConfigError as e:
                raise BadConfigError(['empty']+e.path, e.msg)
            except TypeError as e:
                raise BadConfigError(['empty'], str(e))
        elif no_consecutive_date is not None:
            try:
                self._checker = NoConsecutiveDateChecker(**no_consecutive_date)
            except BadConfigError as e:
                raise BadConfigError(['no_consecutive_date']+e.path, e.msg)
            except TypeError as e:
                raise BadConfigError(['no_consecutive_date'], str(e))
        elif no_more_than_once_a_month is not None:
            try:
                self._checker = NoMoreThanOnceAMonthChecker(
                    **no_more_than_once_a_month)
            except BadConfigError as e:
                raise BadConfigError(
                    ['no_more_than_once_a_month']+e.path, e.msg)
            except TypeError as e:
                raise BadConfigError(['no_more_than_once_a_month'], str(e))
        else:
            raise BadConfigError(
                'at least one checker should be specified for this task. '
                'Available checkers are "unique", "empty", "no_consecutive_date", "no_more_than_once_a_month"'
            )

    def run(self, df: pd.DataFrame) -> bool:
        for sub_df in self._filter.filter(df):
            succeed = self._checker.check(sub_df)
            if not succeed:
                return False
        return True

    @property
    def err_msg(self) -> str:
        return self._checker.err_msg

    @property
    def df(self) -> pd.DataFrame:
        return self._checker.df
