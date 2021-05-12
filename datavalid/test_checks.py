from unittest import TestCase

import pandas as pd

from datavalid.checks import UniqueCheck, EmptyCheck, NoConsecutiveDateCheck


class UniqueCheckTestCase(TestCase):
    def test_check(self):
        columns = ['first', 'last', 'age']
        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=columns)

        self.assertFalse(UniqueCheck('last').check(df))
        self.assertTrue(UniqueCheck(['first', 'last']).check(df))


class EmptyCheckTestCase(TestCase):
    def test_check(self):
        columns = ['first', 'last', 'age']
        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=columns)

        self.assertFalse(EmptyCheck(
            column='first', op='equal', value='john').check(df))
        self.assertTrue(EmptyCheck(
            column='first', op='equal', value='smith').check(df))


class NoConsecutiveDateCheckTestCase(TestCase):
    def test_check(self):
        columns = ['event', 'event_year', 'event_month', 'event_day']

        self.assertFalse(NoConsecutiveDateCheck(date_from={
            'year_column': 'event_year', 'month_column': 'event_month', 'day_column': 'event_day'
        }).check(pd.DataFrame([
            ['officer_join', 2000, 1, 3],
            ['promotion', 2000, 1, 4],
            ['officer_left', 2010, 9, 3],
        ], columns=columns)))

        self.assertTrue(NoConsecutiveDateCheck(date_from={
            'year_column': 'event_year', 'month_column': 'event_month', 'day_column': 'event_day'
        }).check(pd.DataFrame([
            ['officer_join', 2000, 1, 3],
            ['promotion', 2001, 10, 2],
            ['officer_left', 2010, 9, 3],
        ], columns=columns)))
