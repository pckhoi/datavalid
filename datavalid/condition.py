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
    """One or more conditions to filter a table with
    """

    def __init__(
            self,
            column: str or None = None,
            op: str or None = None,
            value: str or int or None = None,
            **kwargs) -> None:
        """Creates new instance of Condition.

        One can create a condition with the following argument combinations:
        - `column`, `op`, and `value`
        - `and`
        - `or`

        `and` and `or` are keywords in Python so they must be suplied by unpacking
        a dictionary.

        Args:
            column (str): column name
            op (str): comparison operator to use. Possible values are
                - equal
                - not_equal
                - greater_than
                - less_than
                - greater_equal
                - less_equal
            value (str or int): the value to compare with
            and (list[dict]):
                list of kwargs each will be passed down to a child Condition object.
                The child conditions will be and-ed together.
            or (list[dict]):
                list of kwargs each will be passed down to a child Condition object.
                The child conditions will be or-ed together.

        Raises:
            BadConfigError: There's a problem with passed-in arguments

        Returns:
            no value
        """
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
        """Creates a boolean series by applying the condition to the provided data.

        Args:
            df (pd.DataFrame): The data to filter on

        Returns:
            A boolean series that can be used to filter or further combined
        """
        if self._conds is not None:
            bool_series = [
                cond.bool_index(df) for cond in self._conds
            ]
            return functools.reduce(self._logic_op, bool_series)
        elif self._column is not None:
            return self._op(df[self._column], self._value)
        return pd.Series([True]*df.shape[0], index=df.index)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter data with the condition.

        Args:
            df (pd.DataFrame): The data to filter on

        Returns:
            The filterd data
        """
        return df.loc[self.bool_index].reset_index(drop=True)
