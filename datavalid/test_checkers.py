from unittest import TestCase

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from datavalid.checkers import (
    UniqueChecker, EmptyChecker, NoConsecutiveDateChecker, NoMoreThanOncePer30DaysChecker, ValidDateChecker
)


class UniqueCheckTestCase(TestCase):
    def test_check(self):
        columns = ['first', 'last', 'age']
        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=columns)

        self.assertTrue(UniqueChecker(['first', 'last']).check(df))

        checker = UniqueChecker('last')
        self.assertFalse(checker.check(df))
        self.assertEqual(checker.err_msg, 'Table contains duplicates')
        assert_frame_equal(checker.df, pd.DataFrame([
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], index=[1, 2], columns=columns))


class EmptyCheckTestCase(TestCase):
    def test_check(self):
        columns = ['first', 'last', 'age']
        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=columns)

        self.assertTrue(EmptyChecker(
            column='first', op='equal', value='smith'
        ).check(df))

        self.assertFalse(EmptyChecker(**{
            'and': [
                {'column': 'last', 'op': 'equal', 'value': 'smith'},
                {'column': 'age', 'op': 'greater_equal', 'value': 30},
            ]
        }).check(df))

        checker = EmptyChecker(column='first', op='equal', value='john')
        self.assertFalse(checker.check(df))
        self.assertEqual(checker.err_msg, 'There are 1 such rows')
        assert_frame_equal(checker.df, pd.DataFrame([
            ['john', 'doe', 23],
        ], columns=columns))


class NoConsecutiveDateCheckTestCase(TestCase):
    def test_check(self):
        columns = ['event', 'event_year', 'event_month', 'event_day']

        self.assertTrue(NoConsecutiveDateChecker(date_from={
            'year_column': 'event_year', 'month_column': 'event_month', 'day_column': 'event_day'
        }).check(pd.DataFrame([
            ['officer_join', 2000, 1, 3],
            ['promotion', 2001, 10, 2],
            ['officer_left', 2010, 9, 3],
        ], columns=columns)))

        checker = NoConsecutiveDateChecker(date_from={
            'year_column': 'event_year', 'month_column': 'event_month', 'day_column': 'event_day'
        })
        self.assertFalse(checker.check(pd.DataFrame([
            ['promotion', 2000, 1, 4],
            ['officer_join', 2000, 1, 3],
            ['officer_left', 2010, 9, 3],
        ], columns=columns)))
        self.assertEqual(checker.err_msg, 'Consecutive dates detected')
        assert_frame_equal(checker.df, pd.DataFrame([
            ['officer_join', 2000, 1, 3],
            ['promotion', 2000, 1, 4],
        ], index=[1, 0], columns=columns))


class NoMoreThanOncePer30DaysCheckerTestCase(TestCase):
    def test_check(self):
        columns = ['event', 'event_year', 'event_month', 'event_day']

        checker = NoMoreThanOncePer30DaysChecker(date_from={
            'year_column': 'event_year', 'month_column': 'event_month', 'day_column': 'event_day'
        })
        self.assertTrue(checker.check(pd.DataFrame([
            ['officer_join', 2000, 1, 3],
            ['promotion', 2001, 10, 2],
            ['officer_left', 2010, 9, 3],
        ], columns=columns)))

        self.assertFalse(checker.check(pd.DataFrame([
            ['promotion', 2000, 1, 4],
            ['officer_join', 2000, 1, 3],
            ['officer_join', 1999, 12, 23],
            ['officer_left', 2010, 9, 3],
        ], columns=columns)))
        self.assertEqual(
            checker.err_msg, '3 rows detected occur too close together')
        assert_frame_equal(checker.df, pd.DataFrame([
            ['officer_join', 1999, 12, 23],
            ['officer_join', 2000, 1, 3],
            ['promotion', 2000, 1, 4],
        ], index=[2, 1, 0], columns=columns))


class ValidDateCheckerTestCase(TestCase):
    def test_check(self):
        columns = ['event', 'event_year', 'event_month', 'event_day']

        checker = ValidDateChecker(date_from={
            'year_column': 'event_year', 'month_column': 'event_month', 'day_column': 'event_day'
        }, min_date='1900-02-03')
        self.assertTrue(checker.check(pd.DataFrame([
            ['officer_join', 2000, 1, 3],
            ['promotion', 2001, 10, np.NaN],
            ['officer_left', 2010, np.NaN, np.NaN],
        ], columns=columns)))

        self.assertFalse(checker.check(pd.DataFrame([
            ['officer_join', 2050, 3, 2],
            ['officer_join', 2000, 4, 3]
        ], columns=columns)))
        self.assertEqual(checker.err_msg, 'future dates detected')
        assert_frame_equal(checker.df, pd.DataFrame([
            ['officer_join', 2050, 3, 2],
        ], columns=columns))

        self.assertFalse(checker.check(pd.DataFrame([
            ['officer_join', 1899, 4, 5],
            ['officer_join', 1900, 1, 2],
            ['officer_join', 1900, 2, 1],
            ['officer_join', 2000, 4, 3]
        ], columns=columns)))
        self.assertEqual(
            checker.err_msg, 'dates less than "1900-02-03" detected')
        assert_frame_equal(checker.df, pd.DataFrame([
            ['officer_join', 1899, 4, 5],
            ['officer_join', 1900, 1, 2],
            ['officer_join', 1900, 2, 1],
        ], columns=columns))
