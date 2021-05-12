from typing import List
import operator
import functools

import pandas as pd


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
            together: List or None = None,
            either_or: List or None = None) -> None:
        self._conds = None
        self._column = None
        if together is not None:
            self._conds = [Condition(**obj) for obj in together]
            self._logic_op = logical_operators['AND']
        elif either_or is not None:
            self._conds = [Condition(**obj) for obj in either_or]
            self._logic_op = logical_operators['OR']
        elif column is not None:
            self._column = column
            self._op = compare_opeartors[op.upper()]
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
