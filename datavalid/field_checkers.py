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

    def to_markdown(self) -> str:
        """Render this quality as markdown text."""
        raise NotImplementedError()


class UniqueFieldChecker(BaseFieldChecker):
    """Checks that column only contain unique values"""

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        return sr[sr.duplicated(keep=False)]

    def to_markdown(self) -> str:
        return "- Unique"


class NoNAFieldChecker(BaseFieldChecker):
    """Checks that column contain no NA value"""

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        return sr[sr.isna()]

    def to_markdown(self) -> str:
        return "- No NA"


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

    def to_markdown(self) -> str:
        return '\n'.join(["- Options:"]+[
            "  - "+opt for opt in self._opts
        ])


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
            return sr[~sr.astype(str).str.match(r'^\d+$') & sr.notna() & (sr.astype(str) != '')]

    def to_markdown(self) -> str:
        return "- Integer"


class FloatFieldChecker(BaseFieldChecker):
    """Checks that column only contain float (or integer) values"""

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        if sr.dtype.name in ['int64', 'float64']:
            return pd.Series([])
        else:
            return sr[~sr.astype(str).str.match(r'^(\d*\.)?\d+$') & sr.notna() & (sr.astype(str) != '')]

    def to_markdown(self) -> str:
        return "- Float"


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

    def to_markdown(self) -> str:
        return "- Range: `%d` -> `%d`" % (self._low, self._high)


class TitleCaseFieldChecker(BaseFieldChecker):
    """Checks that values are in title case
    """

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        return sr[
            sr.notna() & sr.fillna('').astype(str).map(
                lambda x: all([
                    e != '' and e[0].upper() != e[0]
                    for e in x.split(' ')
                ])
            )
        ]

    def to_markdown(self) -> str:
        return "- Title case"


class MatchRegexFieldChecker(BaseFieldChecker):
    """Checks that values match a regex pattern
    """

    def __init__(self, pattern: str) -> None:
        super().__init__()
        self._pattern = pattern

    def _bad_values(self, sr: pd.Series) -> pd.Series:
        return sr[
            sr.notna() &
            ~sr.fillna('').astype(str).str.match(self._pattern)
        ]

    def to_markdown(self) -> str:
        return "<li>Match regexp: <code>%s</code></li>" % self._pattern
