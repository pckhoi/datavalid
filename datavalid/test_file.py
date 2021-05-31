import os
import sys
from unittest import TestCase
from contextlib import redirect_stdout
from tempfile import NamedTemporaryFile
from pathlib import Path
from io import StringIO

import pandas as pd
from pandas.testing import assert_frame_equal

from datavalid.file import File


class FileTestCase(TestCase):
    maxDiff = None

    def test_task_pass(self):
        with NamedTemporaryFile(delete=False) as f:
            pd.DataFrame([
                ['john', 'doe', 23],
                ['jean', 'smith', 43],
                ['jane', 'smith', 30]
            ], columns=['first', 'last', 'age']).to_csv(f, index=False)
            fp = Path(f.name)

        file = File(fp.parent, str(fp), validation_tasks=[
            {
                'name': 'the smiths should have unique first name',
                'where': {'column': 'last', 'op': 'equal', 'value': 'smith'},
                'unique': 'first'
            }
        ], no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            self.assertTrue(file.valid())
            sys.stdout.flush()
        self.assertEqual(buf.getvalue(), '\n'.join([
            'Validating file ' + str(fp),
            '  [32m✓[0m the smiths should have unique first name',
            '',
        ]))

        os.remove(fp)

    def test_task_fail(self):
        with NamedTemporaryFile(delete=False) as f:
            pd.DataFrame([
                ['promotion', 2000, 1, 4],
                ['officer_join', 2000, 1, 3],
                ['officer_left', 2010, 9, 3],
            ], columns=['event', 'event_year', 'event_month', 'event_day']).to_csv(f, index=False)
            fp = Path(f.name)

        file = File(fp.parent, str(fp), validation_tasks=[
            {
                'name': 'no more than one event a month',
                'no_more_than_once_per_30_days': {
                        'date_from': {
                            'year_column': 'event_year', 'month_column': 'event_month', 'day_column': 'event_day'
                        }
                }
            }
        ], no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            self.assertFalse(file.valid())
            sys.stdout.flush()
        self.assertEqual(buf.getvalue(), '\n'.join([
            'Validating file ' + str(fp),
            '  [31m✕[0m no more than one event a month',
            '    2 rows detected occur too close together',
            '              event  event_year  event_month  event_day',
            '    1  officer_join        2000            1          3',
            '    0     promotion        2000            1          4',
            '',
        ]))

        os.remove(fp)

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

        file = File(fp_1.parent, str(fp_1), validation_tasks=[
            {
                    'name': 'last name should be unique',
                    'unique': 'last'
                    }
        ], save_bad_rows_to=str(fp_2), no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            self.assertFalse(file.valid())
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

    def test_validate_schema(self):
        with NamedTemporaryFile(delete=False) as f:
            pd.DataFrame([
                ['john', 'doe', 23],
                ['jean', 'smith', 43],
                ['jane', 'smith', 30]
            ], columns=['first', 'last', 'age']).to_csv(f, index=False)
            fp = Path(f.name)

        file = File(fp.parent, str(fp), schema={
            'age': {'integer': True},
            'last': {'unique': True}
        }, no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            self.assertFalse(file.valid())
            sys.stdout.flush()
        self.assertEqual(buf.getvalue(), '\n'.join([
            'Validating file ' + str(fp),
            '  [31m✕[0m column "last" failed "unique" check. Offending values:',
            '    1    smith',
            '    2    smith',
            '',
        ]))
