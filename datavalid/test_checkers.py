from unittest import TestCase

import pandas as pd

from datavalid.checkers import UniqueChecker, EmptyChecker, NoConsecutiveDateChecker, NoMoreThanOnceAMonthChecker


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
        self.assertEqual(checker.err_msg, '\n'.join([
            'Table contains duplicates',
            '  first   last  age',
            '1  jean  smith   43',
            '2  jane  smith   30',
        ]))


class EmptyCheckTestCase(TestCase):
    def test_check(self):
        columns = ['first', 'last', 'age']
        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=columns)

        self.assertTrue(EmptyChecker(
            column='first', op='equal', value='smith').check(df))

        checker = EmptyChecker(column='first', op='equal', value='john')
        self.assertFalse(checker.check(df))
        self.assertEqual(checker.err_msg, '\n'.join([
            'There are 1 such rows',
            '  first last  age',
            '0  john  doe   23'
        ]))


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
        self.assertEqual(checker.err_msg, '\n'.join([
            'Consecutive dates detected',
            '          event  event_year  event_month  event_day',
            '1  officer_join        2000            1          3',
            '0     promotion        2000            1          4',
        ]))


class NoMoreThanOnceAMonthCheckerTestCase(TestCase):
    def test_check(self):
        columns = ['event', 'event_year', 'event_month', 'event_day']

        checker = NoMoreThanOnceAMonthChecker(date_from={
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
            ['officer_left', 2010, 9, 3],
        ], columns=columns)))
        self.assertEqual(checker.err_msg, '\n'.join([
            'More than 1 row detected in the month Jan, 2000',
            '          event  event_year  event_month  event_day',
            '0     promotion        2000            1          4',
            '1  officer_join        2000            1          3',
        ]))
