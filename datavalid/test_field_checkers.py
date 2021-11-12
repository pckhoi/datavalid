from unittest import TestCase

import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from datavalid.field_checkers import (
    MatchRegexFieldChecker, TitleCaseFieldChecker, UniqueFieldChecker, NoNAFieldChecker, OptionsFieldChecker,
    IntegerFieldChecker, FloatFieldChecker, RangeFieldChecker
)


class UniqueFieldCheckerTestCase(TestCase):
    def test_check(self):
        c = UniqueFieldChecker()
        self.assertIsNone(c.check(pd.Series([1, 2, 3])))
        assert_series_equal(
            c.check(pd.Series([1, 2, 2])),
            pd.Series([2, 2], index=[1, 2])
        )


class NoNAFieldCheckerTestCase(TestCase):
    def test_check(self):
        c = NoNAFieldChecker()
        self.assertIsNone(c.check(pd.Series([1, 2, 3])))
        assert_series_equal(
            c.check(pd.Series([1, np.NaN, 2])),
            pd.Series([np.NaN], index=[1])
        )


class OptionsFieldCheckerTestCase(TestCase):
    def test_check(self):
        c = OptionsFieldChecker('a', 'b', 'c')
        self.assertIsNone(c.check(pd.Series(['a', 'b', 'c'])))
        assert_series_equal(
            c.check(pd.Series(['a', 'b', 'd'])),
            pd.Series(['d'], index=[2])
        )


class IntegerFieldCheckerTestCase(TestCase):
    def test_check(self):
        c = IntegerFieldChecker()

        self.assertIsNone(c.check(pd.Series([1, 2, 0])))
        self.assertIsNone(c.check(pd.Series([3.0, 0, np.NaN])))
        self.assertIsNone(c.check(pd.Series(['3', '400', '0', ''])))

        assert_series_equal(
            c.check(pd.Series([2, 3.0, 4.1, np.NaN])),
            pd.Series([4.1], index=[2])
        )

        assert_series_equal(
            c.check(pd.Series(['a', 2, 3])),
            pd.Series(['a'])
        )

        assert_series_equal(
            c.check(pd.Series(['2', 'a'])),
            pd.Series(['a'], index=[1])
        )


class FloatFieldCheckerTestCase(TestCase):
    def test_check(self):
        c = FloatFieldChecker()

        self.assertIsNone(c.check(pd.Series([1, 2.0, 3.4, np.NaN])))

        assert_series_equal(
            c.check(pd.Series(['a', 2.1, 3, '4.5', '6', ''])),
            pd.Series(['a'])
        )


class RangeFieldCheckerTestCase(TestCase):
    def test_check(self):
        c = RangeFieldChecker(1900, 2020)

        self.assertIsNone(c.check(pd.Series([1991, 2001, 1900, 2020])))

        assert_series_equal(
            c.check(pd.Series([20, 1899, 1970, 2021])),
            pd.Series([20, 1899, 2021], index=[0, 1, 3])
        )


class TitleCaseFieldCheckerTestCase(TestCase):
    def test_check(self):
        c = TitleCaseFieldChecker()

        self.assertIsNone(c.check(pd.Series([
            np.NaN, '', 'John', 'Sullivan Jr', 'Ivan III'
        ])))

        assert_series_equal(
            c.check(pd.Series(["earl", "GREY"])),
            pd.Series(["earl"])
        )


class MatchRegexFieldCheckerTestCase(TestCase):
    def test_check(self):
        c = MatchRegexFieldChecker(r'\d{2}:\d{2}$')

        self.assertIsNone(c.check(pd.Series([
            np.NaN, '10:30', '03:45'
        ])))

        assert_series_equal(
            c.check(pd.Series(['', '1030', '15:03'])),
            pd.Series(['', '1030'])
        )
