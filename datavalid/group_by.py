from typing import Iterator

import pandas as pd


class GroupBy(object):
    def __init__(self, columns: str or list[str] or None = None) -> None:
        if type(columns) is list:
            self._columns = columns
        elif type(columns) is str:
            self._columns = [columns]
        else:
            self._columns = None

    def groups(self, df: pd.DataFrame) -> Iterator[pd.DataFrame]:
        if self._columns is None:
            yield df
        else:
            for _, frame in df.groupby(self._columns):
                yield frame
