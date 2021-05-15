import operator
import functools

import pandas as pd

from .exceptions import BadConfigError


logical_operators = {
    'AND': operator.and_,
    'OR': operator.or_
}


compare_opeartors = {
    'EQUAL': operator.eq,
    'NOT_EQUAL': operator.ne,
    'GREATER_THAN': operator.gt,
    'LESS_THAN': operator.lt,
    'GREATER_EQUAL': operator.ge,
    'LESS_EQUAL': operator.le,
}


class Condition(object):
    def __init__(
            self,
            column: str or None = None,
            op: str or None = None,
            value: str or int or None = None,
            **kwargs) -> None:
        self._conds = None
        self._column = None
        if 'and' in kwargs:
            if type(kwargs['and']) is not list:
                raise BadConfigError(['and'], 'should be a list')
            self._conds = []
            for i, obj in enumerate(kwargs['and']):
                try:
                    self._conds.append(Condition(**obj))
                except BadConfigError as e:
                    raise BadConfigError(['and', i]+e.path, e.msg)
                except TypeError as e:
                    raise BadConfigError(['and', i], str(e))
            self._logic_op = logical_operators['AND']
        elif 'or' in kwargs:
            if type(kwargs['or']) is not list:
                raise BadConfigError(['or'], 'should be a list')
            self._conds = []
            for i, obj in enumerate(kwargs['or']):
                try:
                    self._conds.append(Condition(**obj))
                except BadConfigError as e:
                    raise BadConfigError(['or', i]+e.path, e.msg)
                except TypeError as e:
                    raise BadConfigError(['or', i], str(e))
            self._logic_op = logical_operators['OR']
        else:
            self._column = column
            if self._column is not None:
                if op is None:
                    raise BadConfigError(
                        [], '"op" is not defined. Possible values are "equal", "not_equal", "greater_than", "less_than", "greater_equal", "less_equal".'
                    )
                self._op = compare_opeartors[op.upper()]
                if value is None:
                    raise BadConfigError(
                        [], '"value" is not defined.'
                    )
                self._value = value

    def bool_index(self, df: pd.DataFrame) -> pd.Series:
        if self._conds is not None:
            bool_series = [
                cond.bool_index(df) for cond in self._conds
            ]
            return functools.reduce(self._logic_op, bool_series)
        elif self._column is not None:
            return self._op(df[self._column], self._value)
        return pd.Series([True]*df.shape[0], index=df.index)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.loc[self.bool_index].reset_index(drop=True)
