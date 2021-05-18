import os
import sys
from unittest import TestCase
from contextlib import redirect_stdout
from tempfile import NamedTemporaryFile
from pathlib import Path
from io import StringIO

import pandas as pd
from pandas.testing import assert_frame_equal

from datavalid.config import Config


class ConfigTestCase(TestCase):
    maxDiff = None

    def test_run(self):
        with NamedTemporaryFile(delete=False) as f:
            pd.DataFrame([
                ['john', 'doe', 23],
                ['jean', 'smith', 43],
                ['jane', 'smith', 30]
            ], columns=['first', 'last', 'age']).to_csv(f, index=False)
            fp_1 = Path(f.name)

        with NamedTemporaryFile(delete=False) as f:
            pd.DataFrame([
                ['promotion', 2000, 1, 4],
                ['officer_join', 2000, 1, 3],
                ['officer_left', 2010, 9, 3],
            ], columns=['event', 'event_year', 'event_month', 'event_day']).to_csv(f, index=False)
            fp_2 = Path(f.name)

        conf = Config(fp_1.parent, files={
            str(fp_1): [
                {
                    'name': 'the smiths should have unique first name',
                    'where': {'column': 'last', 'op': 'equal', 'value': 'smith'},
                    'unique': 'first'
                }
            ],
            str(fp_2): [
                {
                    'name': 'no more than one event a month',
                    'no_more_than_once_per_30_days': {
                        'date_from': {
                            'year_column': 'event_year', 'month_column': 'event_month', 'day_column': 'event_day'
                        }
                    }
                }
            ]
        }, no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            conf.run()
            sys.stdout.flush()
        self.assertEqual(buf.getvalue(), '\n'.join([
            'Validating file ' + str(fp_1),
            '  [32m✓[0m the smiths should have unique first name',
            'Validating file ' + str(fp_2),
            '  [31m✕[0m no more than one event a month',
            '    2 rows detected occur too close together',
            '              event  event_year  event_month  event_day',
            '    1  officer_join        2000            1          3',
            '    0     promotion        2000            1          4',
            '',
        ]))

        os.remove(fp_1)
        os.remove(fp_2)

    def test_save_bad_rows_to(self):
        with NamedTemporaryFile(delete=False) as f:
            pd.DataFrame([
                ['john', 'doe', 23],
                ['jean', 'smith', 43],
                ['jane', 'smith', 30]
            ], columns=['first', 'last', 'age']).to_csv(f, index=False)
            fp_1 = Path(f.name)

        with NamedTemporaryFile(delete=False) as f:
            fp_2 = Path(f.name)

        conf = Config(fp_1.parent, files={
            str(fp_1): [
                {
                    'name': 'last name should be unique',
                    'unique': 'last'
                }
            ]
        }, save_bad_rows_to=str(fp_2), no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            conf.run()
            sys.stdout.flush()
        self.assertEqual(buf.getvalue(), '\n'.join([
            'Validating file ' + str(fp_1),
            '  [31m✕[0m last name should be unique',
            '    Table contains duplicates',
            '    Saved bad rows to ' + str(fp_2),
            '',
        ]))

        assert_frame_equal(pd.read_csv(fp_2), pd.DataFrame([
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=['first', 'last', 'age']))

        os.remove(fp_1)
        os.remove(fp_2)
