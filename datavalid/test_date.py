import datetime

from unittest import TestCase

import pandas as pd
from pandas.testing import assert_series_equal

from datavalid.date import DateParser


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
        assert_series_equal(
            parser.parse(df),
            pd.Series([
                datetime.datetime(2000, 1, 3),
                datetime.datetime(2001, 10, 2),
                datetime.datetime(2010, 9, 3),
            ]),
            check_names=False
        )
