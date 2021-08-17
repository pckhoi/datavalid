import datetime

import pandas as pd

from .exceptions import BadConfigError, BadDateError


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

    def parse(self, df: pd.DataFrame) -> pd.DataFrame:
        """Produces a date dataframe (including date, year, month, day column) from the given data.

        Args:
            df (pd.DataFrame): data to derive date from

        Raises:
            BadDateError: Impossible dates detected

        Returns:
            a date dataframe
        """
        today = datetime.date.today()
        year = df[self._year].astype('Int64')
        month = df[self._month].astype('Int64')
        day = df[self._day].astype('Int64')

        rows = df.loc[month.notna() & ((month < 1) | (month > 12))]
        if rows.shape[0] > 0:
            raise BadDateError('impossible months detected', rows)

        rows = df.loc[
            (year > today.year)
            | (
                (year == today.year)
                & (
                    (month.notna() & (month > today.month))
                    | (day.notna() & (month == today.month) & (day > today.day))
                )
            )
        ]
        if rows.shape[0] > 0:
            raise BadDateError('future dates detected', rows)

        rows = df.loc[day < 0]
        if rows.shape[0] > 0:
            raise BadDateError('negative days detected', rows)

        leap_year = (year % 400 == 0) | ((year % 4 == 0) & (year % 100 != 0))
        rows = df.loc[
            (month.isin([1, 3, 5, 7, 8, 10, 12]) & (day > 31))
            | (month.isin([4, 6, 9, 11]) & (day > 30))
            | ((month == 2) & (
                (~leap_year & (day > 28))
                | (leap_year & (day > 29))
            ))
        ]
        if rows.shape[0] > 0:
            raise BadDateError('impossible dates detected', rows)

        dates = df[[self._year, self._month, self._day]]
        dates.columns = ["year", "month", "day"]
        dates.loc[:, 'date'] = pd.to_datetime(dates)
        for col in ["year", "month", "day"]:
            dates.loc[:, col] = dates[col].astype('Int64')
        return dates


def parse_single_date(date_str: str) -> datetime.datetime:
    """Parses date value and raise error if format isn't right

    Args:
        date_str (str): date string in format YYYY-MM-DD

    Raises:
        BadConfigError: date_str is not a string or format is wrong.

    Returns:
        parsed datetime
    """
    if type(date_str) is not str:
        raise BadConfigError(
            [], 'date must be a string matching format "YYYY-MM-DD"',
        )
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError as e:
        raise BadConfigError([], 'date must match format "YYYY-MM-DD"')
