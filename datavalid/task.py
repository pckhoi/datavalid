import pandas as pd

from .checkers import (
    NoMoreThanOncePer30DaysChecker, UniqueChecker, EmptyChecker, NoConsecutiveDateChecker, ValidDateChecker
)
from .filter import Filter
from .exceptions import BadConfigError, TaskValidationError


class Task(object):
    """Defines and performs validation task on the given data.

    Attributes:
        err_msg (str):
            error message, available if run() returns False
        df (pd.DataFrame):
            offending rows, available if run() returns False
        warn_only (bool):
            if true then failing this validation will only
            generate a warning rather than failing the whole
            run
    """

    warn_only: bool

    def __init__(
        self,
        name: str or None = None,
        where: dict or None = None,
        group_by: str or None = None,
        unique: str or list[str] or None = None,
        empty: dict or None = None,
        no_consecutive_date: dict or None = None,
        no_more_than_once_per_30_days: dict or None = None,
        valid_date: dict or None = None,
        warn_only: bool = False
    ) -> None:
        """Creates a new instance of Task

        Of all the keyword arguments, `unique`, `empty`, `no_consecutive_date`
        and `no_more_than_once_per_30_days` are exclusive. Which mean exactly
        one of them must be passed in. They define which checker to use for
        this task.

        Args:
            name (str):
                name of task. Always required.
            where (dict):
                the `where` argument used to create a Filter object.
            group_by (dict):
                the `group_by` argument used to create a Filter object.
            unique (str or list[str]):
                if defined, this task's checker will be a UniqueChecker with
                this argument passed in as `columns` argument to UniqueChecker.
            empty (dict):
                if defined, this task's checker will be an EmptyChecker with
                this argument passed in as keyword arguments to EmptyChecker.
            no_consecutive_date (dict):
                if defined, this task's checker will be a NoConsecutiveDateChecker
                with this argument passed in as keyword arguments to
                NoConsecutiveDateChecker.
            no_more_than_once_per_30_days (dict):
                if defined, this task's checker will be a NoMoreThanOncePer30DaysChecker
                with this argument passed in as keyword arguments to
                NoMoreThanOncePer30DaysChecker.
            valid_date (dict):
                if defined, this task's checker will be a ValidDateChecker with this
                argument passed in as keyword arguments to ValidDateChecker.
            warn_only (bool):
                if set to true then failing this validation will only generate a warning
                rather than failing the whole run.

        Raises:
            BadConfigError: There's a problem with passed-in arguments

        Returns:
            no value
        """
        if name is None:
            raise BadConfigError(
                [],
                'task must have a name specified with "name" key'
            )
        self.name = name
        self.warn_only = warn_only
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
        elif no_more_than_once_per_30_days is not None:
            try:
                self._checker = NoMoreThanOncePer30DaysChecker(
                    **no_more_than_once_per_30_days)
            except BadConfigError as e:
                raise BadConfigError(
                    ['no_more_than_once_per_30_days']+e.path, e.msg)
            except TypeError as e:
                raise BadConfigError(['no_more_than_once_per_30_days'], str(e))
        elif valid_date is not None:
            try:
                self._checker = ValidDateChecker(
                    **valid_date)
            except BadConfigError as e:
                raise BadConfigError(
                    ['valid_date']+e.path, e.msg)
            except TypeError as e:
                raise BadConfigError(['valid_date'], str(e))
        else:
            raise BadConfigError(
                'at least one checker should be specified for this task. '
                'Available checkers are "unique", "empty", "no_consecutive_date", "no_more_than_once_per_30_days"'
            )

    def run(self, df: pd.DataFrame) -> None:
        """Run validation task and raise an error if not succeed.

        Args:
            df (pd.DataFrame):
                the data to validate

        Raises:
            TaskValidationError: validation task failed

        Returns:
            no value
        """
        for sub_df in self._filter.filter(df):
            if not self._checker.check(sub_df):
                raise TaskValidationError(
                    self.name, self._err_msg, self._df, self.warn_only)

    @property
    def _err_msg(self) -> str:
        return self._checker.err_msg

    @property
    def _df(self) -> pd.DataFrame:
        return self._checker.df

    def to_markdown(self) -> str:
        """Render this task as markdown"""
        return "- %s" % self.name
