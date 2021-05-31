import pandas as pd

from .exceptions import BadConfigError


class BaseFieldChecker(object):
    """Base class for all field checker classes

    Field checker checks that a column (pandas series) satisfy
    a condition
    """

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        raise NotImplementedError()

    def check(self, sr: pd.Series) -> pd.Series or None:
        """Checks whether series satisfy condition

        Args:
            sr (pd.Series):
                the series to check

        Returns:
            None if there's nothing wrong, otherwise it will
            return the offending values in a series
        """
        sr = self._bad_values(sr)
        if sr.size == 0:
            return None
        return sr


class UniqueFieldChecker(BaseFieldChecker):
    """Checks that column only contain unique values"""

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        return sr[sr.duplicated(keep=False)]


class NotEmptyFieldChecker(BaseFieldChecker):
    """Checks that column contain no NA value"""

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        return sr[sr.isna()]


class OptionsFieldChecker(BaseFieldChecker):
    """Checks that column only contains values specified"""

    def __init__(self, *options: list[str]) -> None:
        """Creates a new instance of OptionsFieldChecker

        Args:
            *options (list of str):
                valid values for this column

        Returns:
            no value
        """
        super().__init__()
        if not all([type(opt) is str for opt in options]):
            raise BadConfigError([], 'must be a list of strings')
        self._opts = set(options)

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        return sr[~sr.isin(self._opts) & sr.notna()]


class IntegerFieldChecker(BaseFieldChecker):
    """Checks that column only contain integer values"""

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        if sr.dtype.name == 'int64':
            return pd.Series([])
        elif sr.dtype.name == 'float64':
            return sr[sr.mod(1) > 0]
        else:
            # dtype is probably 'object' with strings in it
            # return the strings
            return sr[sr.str.match('').notna()]


class FloatFieldChecker(BaseFieldChecker):
    """Checks that column only contain float (or integer) values"""

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        if sr.dtype.name in ['int64', 'float64']:
            return pd.Series([])
        else:
            return sr[sr.str.match('').notna()]


class RangeFieldChecker(FloatFieldChecker):
    """Checks that column only contain values in a range

    It is implied that values must also be float or integer
    """

    def __init__(self, low: int or float, high: int or float) -> None:
        """Creates a new instance of RangeFieldChecker

        Args:
            low (int or float):
                minimum valid value
            high (int or float):
                maximum valid value

        Returns:
            no value
        """
        super().__init__()
        if type(low) not in [int, float] or type(high) not in [int, float]:
            raise BadConfigError('must be 2 numbers')
        self._low = low
        self._high = high

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        res = super()._bad_values(sr)
        if res.size > 0:
            return res
        return sr[(sr < self._low) | (sr > self._high)]
