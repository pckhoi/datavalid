import pandas as pd

from .exceptions import BadConfigError


class DateParser(object):
    """Parse dates from a table.
    """

    def __init__(self, year_column: str or None = None, month_column: str or None = None, day_column: str or None = None) -> None:
        """Creates a new instance of DateParser

        Args:
            year_column (str): year column name
            month_column (str): month column name
            day_column (str): day column name

        Raises:
            BadConfigError: There's a problem with passed-in arguments

        Returns:
            no value
        """
        if year_column is None or type(year_column) is not str:
            raise BadConfigError([], '"year_column" should be a column name')
        self._year = year_column
        if month_column is None or type(month_column) is not str:
            raise BadConfigError([], '"month_column" should be a column name')
        self._month = month_column
        if day_column is None or type(day_column) is not str:
            raise BadConfigError([], '"day_column" should be a column name')
        self._day = day_column

    def parse(self, df: pd.DataFrame) -> pd.Series:
        """Produces a date series from the given data.

        Args:
            df (pd.DataFrame): data to derive date from

        Returns:
            a date series
        """
        dates = df[[self._year, self._month, self._day]]
        dates.columns = ["year", "month", "day"]
        return pd.to_datetime(dates)
