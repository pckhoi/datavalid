from typing import Iterator

import pandas as pd

from .condition import Condition
from .group_by import GroupBy


class Filter(object):
    def __init__(self, where: dict = None, group_by: str or list = None) -> None:
        if where is not None:
            self._condition = Condition(**where)
        else:
            self._condition = Condition()   # no-op condition
        if group_by is not None:
            self._group_by = GroupBy(group_by)
        else:
            self._group_by = GroupBy()

    def filter(self, df: pd.DataFrame) -> Iterator[pd.DataFrame]:
        df = self._condition.apply(df)
        for sub_df in self._group_by.groups(df):
            yield sub_df
