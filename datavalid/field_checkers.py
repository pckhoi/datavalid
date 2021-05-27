import pandas as pd

from .exceptions import BadConfigError


class BaseFieldChecker(object):
    def _bad_values(self, sr: pd.Series) -> pd.Series:
        raise NotImplementedError()

    def check(self, sr: pd.Series) -> pd.Series or None:
        sr = self._bad_values(sr)
        if sr.size == 0:
            return None
        return sr


class UniqueFieldChecker(BaseFieldChecker):
    def _bad_values(self, sr: pd.Series) -> pd.Series:
        return sr.duplicated(keep=False)


class NotEmptyFieldChecker(object):
    def _bad_values(self, sr: pd.Series) -> pd.Series:
        return sr[sr.isna()]


class OptionsFieldChecker(object):
    def __init__(self, *options: list[str]) -> None:
        super().__init__()
        if not all([type(opt) is str for opt in options]):
            raise BadConfigError([], 'must be a list of strings')
        self._opts = set(options)

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        return sr[~sr.isin(self._opts) & sr.notna()]


class IntegerFieldChecker(object):
    def _bad_values(self, sr: pd.Series) -> pd.Series:
        if sr.dtype.name == 'int64':
            return pd.Series([])
        elif sr.dtype.name == 'float64':
            return sr[sr.mod(1) > 0]
        else:
            return sr[sr.str.match('').notna()]


class FloatFieldChecker(object):
    def _bad_values(self, sr: pd.Series) -> pd.Series:
        if sr.dtype.name in ['int64', 'float64']:
            return pd.Series([])
        else:
            return sr[sr.str.match('').notna()]


class RangeFieldChecker(object):
    def __init__(self, low: int or float, high: int or float) -> None:
        super().__init__()
        if type(low) not in [int, float] or type(high) not in [int, float]:
            raise BadConfigError('must be 2 numbers')
        self._low = low
        self._high = high

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        return sr[(sr < self._low) | (sr > self._high)]
