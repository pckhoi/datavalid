from typing import Type

import pandas as pd

from .exceptions import BadConfigError
from .field_checkers import (
    BaseFieldChecker, UniqueFieldChecker, NotEmptyFieldChecker, OptionsFieldChecker,
    IntegerFieldChecker, FloatFieldChecker, RangeFieldChecker
)


checker_dict = {
    'unique': UniqueFieldChecker,
    'not_empty': NotEmptyFieldChecker,
    'options': OptionsFieldChecker,
    'integer': IntegerFieldChecker,
    'float': FloatFieldChecker,
    'range': RangeFieldChecker
}


class FieldSchema(object):
    _desc: str or None
    _checkers: dict[str, Type[BaseFieldChecker]]
    attrs: dict
    failed_check: str
    sr: pd.Series

    def __init__(self, description: str or None = None, **kwargs) -> None:
        self._desc = description
        self._checkers = dict()
        for k, v in sorted(kwargs.items(), key=lambda tup: tup[1]):
            if k not in checker_dict:
                raise BadConfigError([], 'unknown option %s' % k)
            try:
                if v == True:
                    self._checkers[k] = checker_dict[k]()
                elif type(v) is list:
                    self._checkers[k] = checker_dict[k](*v)
                else:
                    raise BadConfigError([k], 'invalid option')
            except BadConfigError as e:
                raise BadConfigError([k]+e.path, e.msg)
        self.attrs = kwargs

    def validate(self, sr: pd.Series) -> bool:
        for name, checker in self._checkers.items():
            res = checker.check(sr)
            if res is not None:
                self.sr = res
                self.failed_check = name
                return False
        return True
