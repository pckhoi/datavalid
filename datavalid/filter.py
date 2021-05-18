from typing import Iterator, List

import pandas as pd

from .condition import Condition
from .group_by import GroupBy
from .exceptions import BadConfigError


class Filter(object):
    """Filters data based on given condition grouped by given `group_by`
    """

    def __init__(self, where: dict = None, group_by: str or List[str] or None = None) -> None:
        """Creates a new instance of Filter

        Args:
            where (dict):
                keyword arguments that will be passed to Condition().
                This is the condition to filter with. If not set then
                the date will be unfiltered.
            group_by (str or list[str]):
                list of columns to group data with. If not given then
                data will be treated as one single group.

        Raises:
            BadConfigError: There's a problem with passed-in arguments

        Returns:
            no value
        """
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
        """Filters given data and emit data in groups.

        Args:
            df (pd.DataFrame): the data to filter

        Returns:
            an iterator of data frames. Each element is a group already filtered.
        """
        df = self._condition.apply(df)
        for sub_df in self._group_by.groups(df):
            yield sub_df
