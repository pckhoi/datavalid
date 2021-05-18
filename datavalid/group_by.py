from typing import Iterator

import pandas as pd


class GroupBy(object):
    """Divides data into groups.
    """

    def __init__(self, columns: str or list[str] or None = None) -> None:
        """Creates a new instance of GroupBy

        Args:
            columns (str or list[str]):
                list of columns to group by. If not given then the whole
                data frame is treated as one group

        Returns:
            no value
        """
        if type(columns) is list:
            self._columns = columns
        elif type(columns) is str:
            self._columns = [columns]
        else:
            self._columns = None

    def groups(self, df: pd.DataFrame) -> Iterator[pd.DataFrame]:
        """Divides the given data into groups and returns them as an iterator

        Args:
            df (pd.DataFrame): the data to be divided

        Returns:
            an iterator of data groups
        """
        if self._columns is None:
            yield df
        else:
            for _, frame in df.groupby(self._columns):
                yield frame
