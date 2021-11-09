from typing import Type

import pandas as pd

from .exceptions import BadConfigError, ColumnValidationError
from .field_checkers import (
    BaseFieldChecker, MatchRegexFieldChecker, TitleCaseFieldChecker, UniqueFieldChecker, NoNAFieldChecker, OptionsFieldChecker,
    IntegerFieldChecker, FloatFieldChecker, RangeFieldChecker
)


checker_dict = {
    'unique': UniqueFieldChecker,
    'no_na': NoNAFieldChecker,
    'options': OptionsFieldChecker,
    'integer': IntegerFieldChecker,
    'float': FloatFieldChecker,
    'range': RangeFieldChecker,
    'title_case': TitleCaseFieldChecker,
    'match_regex': MatchRegexFieldChecker
}


class ColumnSchema(object):
    """Describes a column and validates it

    Attributes:
        failed_check (str):
            available if valid() is False, name of the attribute
            that this column failed
        sr (pd.Series):
            available if valid() is False, the offending values
            as a series
    """
    _desc: str or None
    _name: str
    _checkers: dict[str, Type[BaseFieldChecker]]
    failed_check: str
    sr: pd.Series

    def __init__(self, name: str, description: str or None = None, **kwargs) -> None:
        """Creates a new instance of FieldSchema

        Args:
            name (str):
                name of this column
            description (str):
                description of this column
            unique (bool):
                whether this column can only contain unique values
            no_na (bool):
                whether this column can only contain non-NA values
            options (list of str):
                if given then this column can only contain values
                within this list
            integer (bool):
                whether this column can only contain integer values
            float (bool):
                whether this column can only contain float (and
                integer) values
            range (list of 2 numbers):
                ensure values in this column must be numeric and
                must be between the 2 specified values

        Returns:
            no value
        """
        self._name = name
        self._desc = None if description is None else description.strip()
        self._checkers = dict()
        for k, v in kwargs.items():
            if k not in checker_dict:
                raise BadConfigError([], 'unknown option %s' % k)
            try:
                if v == True:
                    self._checkers[k] = checker_dict[k]()
                elif type(v) is list:
                    self._checkers[k] = checker_dict[k](*v)
                elif type(v) is str:
                    self._checkers[k] = checker_dict[k](v)
                else:
                    raise BadConfigError([k], 'invalid option')
            except BadConfigError as e:
                raise BadConfigError([k]+e.path, e.msg)

    def validate(self, sr: pd.Series) -> None:
        """Checks whether this column's values are all valid

        Args:
            sr (pd.Series):
                the series to check

        Raises:
            FieldValidationError: column is not valid

        Returns:
            no value
        """
        for name, checker in self._checkers.items():
            res = checker.check(sr)
            if res is not None:
                raise ColumnValidationError(self._name, name, res)
        return True

    def to_markdown(self) -> str:
        """Render this field schema as markdown."""
        return "\n".join(filter(None, [
            "- **%s**:" % self._name,
            None if self._desc is None else "  - Description: %s\n" % self._desc,
            None if len(self._checkers) == 0 else "\n".join(
                ["  - Attributes:"]+[
                    "    "+checker.to_markdown().replace("\n", "\n    ")
                    for checker in self._checkers.values()
                ]+[""]
            )
        ]))
