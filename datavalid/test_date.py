import datetime

from unittest import TestCase

import pandas as pd
from pandas.testing import assert_frame_equal
import time_machine

from datavalid.date import DateParser, parse_single_date
from datavalid.exceptions import BadConfigError, BadDateError


@time_machine.travel(datetime.datetime(2021, 8, 17))
class DateParserTestCase(TestCase):
    def test_parse(self):
        columns = ['event', 'event_year', 'event_month', 'event_day']
        df = pd.DataFrame([
            ['officer_join', 2000, 1, 3],
            ['promotion', 2001, 10, 2],
            ['officer_left', 2010, 9, 3],
        ], columns=columns)

        parser = DateParser(
            year_column='event_year', month_column='event_month', day_column='event_day')
        assert_frame_equal(
            parser.parse(df),
            pd.DataFrame([
                [2000, 1, 3, datetime.datetime(2000, 1, 3)],
                [2001, 10, 2, datetime.datetime(2001, 10, 2)],
                [2010, 9, 3, datetime.datetime(2010, 9, 3)],
            ], columns=['year', 'month', 'day', 'date'])
            .astype({
                'year': 'Int64',
                'month': 'Int64',
                'day': 'Int64',
                'date': 'datetime64[ns]',
            }),
            check_names=False,
        )

        with self.assertRaises(BadDateError) as cm:
            parser.parse(pd.DataFrame([
                ['officer_join', 2000, 0, 2],
                ['officer_join', 2000, 13, 1],
                ['officer_join', 2000, 4, 3]
            ], columns=columns))
        self.assertEqual(cm.exception.msg, 'impossible months detected')
        assert_frame_equal(cm.exception.rows, pd.DataFrame([
            ['officer_join', 2000, 0, 2],
            ['officer_join', 2000, 13, 1],
        ], columns=columns))

        with self.assertRaises(BadDateError) as cm:
            parser.parse(pd.DataFrame([
                ['officer_join', 2050, 3, 2],
                ['officer_join', 2021, 9, 10],
                ['officer_join', 2021, 8, 20],
                ['officer_join', 2000, 4, 3]
            ], columns=columns))
        self.assertEqual(cm.exception.msg, 'future dates detected')
        assert_frame_equal(cm.exception.rows, pd.DataFrame([
            ['officer_join', 2050, 3, 2],
            ['officer_join', 2021, 9, 10],
            ['officer_join', 2021, 8, 20],
        ], columns=columns))

        with self.assertRaises(BadDateError) as cm:
            parser.parse(pd.DataFrame([
                ['officer_join', 2000, 1, -2],
                ['officer_join', 2000, 4, 3]
            ], columns=columns))
        self.assertEqual(cm.exception.msg, 'negative days detected')
        assert_frame_equal(cm.exception.rows, pd.DataFrame([
            ['officer_join', 2000, 1, -2],
        ], columns=columns))

        with self.assertRaises(BadDateError) as cm:
            parser.parse(pd.DataFrame([
                ['officer_join', 2000, 1, 50],
                ['officer_join', 2000, 4, 31],
                ['officer_join', 2000, 2, 30],
                ['officer_join', 1999, 2, 29],
                ['officer_join', 1900, 2, 29],
                ['officer_join', 2000, 4, 3]
            ], columns=columns))
        self.assertEqual(cm.exception.msg, 'impossible dates detected')
        assert_frame_equal(cm.exception.rows, pd.DataFrame([
            ['officer_join', 2000, 1, 50],
            ['officer_join', 2000, 4, 31],
            ['officer_join', 2000, 2, 30],
            ['officer_join', 1999, 2, 29],
            ['officer_join', 1900, 2, 29],
        ], columns=columns))


class ParseSingleDateTestCase(TestCase):
    def test_parse_single_date(self):
        with self.assertRaises(BadConfigError) as cm:
            parse_single_date(None)
        self.assertEqual(cm.exception.path, [])
        self.assertEqual(cm.exception.msg,
                         'date must be a string matching format "YYYY-MM-DD"')

        with self.assertRaises(BadConfigError) as cm:
            parse_single_date('abcd')
        self.assertEqual(cm.exception.path, [])
        self.assertEqual(cm.exception.msg,
                         'date must match format "YYYY-MM-DD"')

        self.assertEqual(parse_single_date('2001-02-03'),
                         datetime.datetime(2001, 2, 3))
