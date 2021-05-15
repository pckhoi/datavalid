from typing import Iterator, List

import pandas as pd

from .condition import Condition
from .group_by import GroupBy
from .exceptions import BadConfigError


class Filter(object):
    def __init__(self, where: dict = None, group_by: str or List[str] or None = None) -> None:
        if where is not None:
            if type(where) is not dict:
                raise BadConfigError(['where'], 'should be a dict')
            try:
                self._condition = Condition(**where)
            except BadConfigError as e:
                raise BadConfigError(['where']+e.path, e.msg)
            except TypeError as e:
                raise BadConfigError(['where'], str(e))
        else:
            self._condition = Condition()   # no-op condition
        try:
            self._group_by = GroupBy(group_by)
        except BadConfigError as e:
            raise BadConfigError(['group_by']+e.path, e.msg)
        except TypeError as e:
            raise BadConfigError(['group_by'], str(e))

    def filter(self, df: pd.DataFrame) -> Iterator[pd.DataFrame]:
        df = self._condition.apply(df)
        for sub_df in self._group_by.groups(df):
            yield sub_df
