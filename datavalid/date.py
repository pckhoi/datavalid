import pandas as pd


class DateParser(object):
    def __init__(self, year_column: str, month_column: str, day_column: str) -> None:
        self._year = year_column
        self._month = month_column
        self._day = day_column

    def parse(self, df: pd.DataFrame) -> pd.Series:
        dates = df[[self._year, self._month, self._day]]
        dates.columns = ["year", "month", "day"]
        return pd.to_datetime(dates)
