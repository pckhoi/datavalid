import pandas as pd
from termcolor import colored

from .utils import indent


class BadConfigError(Exception):
    """Raised when config object (a dictionary) has error

    This error also records the `path` of where in the object the error
    has occured.

    Attributes
        path (list[str or int]):
            path of the offending field
        msg (str):
            the error message at `path`
    """
    path: list[str or int]
    msg: str

    def __init__(self, path: list[str or int], msg: str) -> None:
        """Creates a new instance of BadConfigError

        Args:
            path (list[str or int]):
                path of offending field. Path may be an empty list if
                the error message is not nested deep inside the config
                object.
            msg (str):
                the error message at `path`.

        Returns:
            no value
        """
        super().__init__(path, msg)
        self.path = path
        self.msg = msg

    def __str__(self) -> str:
        if len(self.path) == 0:
            return self.msg
        sl = list()
        for key in self.path:
            if type(key) is int:
                sl.append('[%d]' % key)
            elif ' ' in str(key):
                sl.append('."%s"' % key)
            else:
                sl.append('.%s' % key)
        return 'error at %s: %s' % (''.join(sl), self.msg)


class BadDateError(ValueError):
    """Raised when rows with invalid dates are detected

    Attributes
        msg (str):
            the error message
        rows (pd.DataFrame):
            rows with invalid dates
    """
    msg: str
    rows: pd.DataFrame

    def __init__(self, msg: str, rows: pd.DataFrame) -> None:
        """Creates a new instance of BadDateError

        Args:
            msg (str):
                the error message
            rows (pd.DataFrame):
                rows with invalid dates

        Returns:
            no value
        """
        super().__init__(msg)
        self.msg = msg
        self.rows = rows


class ColumnError(ValueError):
    """Raised when column error is detected

    Attributes
        msg (str):
            the error message
        column (str):
            the column name
    """
    msg: str
    column: str

    def __init__(self, column: str, msg: str) -> None:
        """Creates a new instance of ColumnError

        Args:
            column (str):
                the column name
            msg (str):
                the error message

        Returns:
            no value
        """
        super().__init__('%s: %s' % (column, msg))
        self.column = column
        self.msg = msg


class ColumnValidationError(ColumnError):
    """Raised when a column does not match schema

    Attributes
        values (pd.Series):
            unique values in the column that violate schema
        failed_check (str):
            name of the failed check
    """
    values: pd.Series
    failed_check: str

    def __init__(self, column: str, failed_check: str, series: pd.Series) -> None:
        """Creates a new instance of ColumnValidationError

        Args:
            column (str):
                the column name
            failed_check (str):
                name of the failed check
            series (pd.Series):
                values that violate schema

        Returns:
            no value
        """
        values = series.drop_duplicates().reset_index(drop=True)
        msg = 'failed %s check. %s offending values:\n%s' % (
            colored(failed_check, "magenta"),
            colored(len(values), "cyan"),
            indent(values.to_string(), 2),
        )
        super().__init__(column, msg)
        self.values = values
        self.failed_check = failed_check


class ColumnMissingError(ColumnError):
    """Raised when a column is present in schema but missing in frame
    """

    def __init__(self, column: str) -> None:
        """Creates a new instance of ColumnMissingError

        Args:
            column (str):
                the column name

        Returns:
            no value
        """
        super().__init__(column, 'is not present')


class TaskValidationError(ValueError):
    """Raised when a validation task fail

    Attributes
        task_name (str):
            name of validation tasks
        err_msg (str):
            the error message
        rows (pd.DataFrame)
            violating rows
        warn (bool):
            whether this error should fail the whole run
    """
    task_name: str
    err_msg: str
    rows: pd.DataFrame
    warn: bool

    def __init__(self, task_name: str, err_msg: str, rows: pd.DataFrame, warn: bool = False) -> None:
        """Creates a new instance of TaskValidationError

        Args:
            task_name (str):
                name of validation tasks
            err_msg (str):
                the error message
            rows (pd.DataFrame)
                violating rows
            warn (bool):
                whether this error should fail the whole run

        Returns:
            no value
        """
        super().__init__('task %s: %s\n%s' % (
            task_name, err_msg, rows.to_string()
        ))
        self.task_name = task_name
        self.err_msg = err_msg
        self.rows = rows
        self.warn = warn
