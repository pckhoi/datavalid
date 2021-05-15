import os
import sys
from unittest import TestCase
from contextlib import redirect_stdout
from tempfile import NamedTemporaryFile
from pathlib import Path
from io import StringIO

import pandas as pd

from datavalid.config import Config


class ConfigTestCase(TestCase):
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
                    'no_more_than_once_a_month': {
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
            'File ' + str(fp_1),
            '  [32m✓[0m the smiths should have unique first name',
            'File ' + str(fp_2),
            '  [31m✕[0m no more than one event a month',
            '    More than 1 row detected in the month Jan, 2000',
            '              event  event_year  event_month  event_day',
            '    0     promotion        2000            1          4',
            '    1  officer_join        2000            1          3',
            '',
        ]))

        os.remove(fp_1)
        os.remove(fp_2)
