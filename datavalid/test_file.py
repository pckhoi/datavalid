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
from datavalid.schema import Schema


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

        file = File(fp.parent, str(fp), schema=Schema('person', validation_tasks=[
            {
                'name': 'the smiths should have unique first name',
                'where': {'column': 'last', 'op': 'equal', 'value': 'smith'},
                'unique': 'first'
            }
        ]), no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            self.assertTrue(file.valid())
            sys.stdout.flush()
        self.assertEqual(buf.getvalue(), '\n'.join([
            'Validating ' + str(fp),
            '  [32m✓ the smiths should have unique first name[0m',
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

        file = File(fp.parent, str(fp), schema=Schema('person', validation_tasks=[
            {
                'name': 'no more than one event a month',
                'no_more_than_once_per_30_days': {
                        'date_from': {
                            'year_column': 'event_year', 'month_column': 'event_month', 'day_column': 'event_day'
                        }
                }
            }
        ]), no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            self.assertFalse(file.valid())
            sys.stdout.flush()
        self.assertEqual(buf.getvalue(), '\n'.join([
            'Validating ' + str(fp),
            '  [31m✕ no more than one event a month[0m',
            '    2 rows detected occur too close together',
            '              event  event_year  event_month  event_day',
            '    1  officer_join        2000            1          3',
            '    0     promotion        2000            1          4',
            '',
        ]))

        os.remove(fp)

    def test_task_exception(self):
        with NamedTemporaryFile(delete=False) as f:
            pd.DataFrame([
                ['promotion', 2000, 1],
                ['officer_join', 2000, 1],
                ['officer_left', 2010, 9],
            ], columns=['event', 'event_year', 'event_month']).to_csv(f, index=False)
            fp = Path(f.name)

        file = File(fp.parent, str(fp), schema=Schema('person', validation_tasks=[
            {
                'name': 'no more than one event a month',
                'no_more_than_once_per_30_days': {
                        'date_from': {
                            'year_column': 'event_year', 'month_column': 'event_month', 'day_column': 'event_day'
                        }
                }
            }
        ]), no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            self.assertFalse(file.valid())
            sys.stdout.flush()
        self.assertTrue(buf.getvalue().startswith('\n'.join([
            'Validating ' + str(fp),
            '  [31m✕ no more than one event a month[0m',
            '    an error occured during task execution: KeyError: \'event_day\''
        ])))

        os.remove(fp)

    def test_task_warn(self):
        with NamedTemporaryFile(delete=False) as f:
            pd.DataFrame([
                ['john', 'doe', 23],
                ['jean', 'smith', 43],
                ['jane', 'smith', 30]
            ], columns=['first', 'last', 'age']).to_csv(f, index=False)
            fp = Path(f.name)

        file = File(fp.parent, str(fp), schema=Schema('person', validation_tasks=[
            {
                'name': 'the smiths should be younger than 30',
                'empty': {
                    'and': [
                        {'column': 'last', 'op': 'equal', 'value': 'smith'},
                        {'column': 'age', 'op': 'greater_equal', 'value': 30},
                    ],
                },
                'warn_only': True
            }
        ]), no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            self.assertTrue(file.valid())
            sys.stdout.flush()
        self.assertEqual(buf.getvalue(), '\n'.join([
            'Validating ' + str(fp),
            '  [33m⚠ the smiths should be younger than 30[0m',
            '    There are 2 such rows',
            '      first   last  age',
            '    0  jean  smith   43',
            '    1  jane  smith   30',
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

        file = File(fp_1.parent, str(fp_1), schema=Schema('person', validation_tasks=[
            {
                    'name': 'last name should be unique',
                    'unique': 'last'
                    }
        ]), save_bad_rows_to=str(fp_2), no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            self.assertFalse(file.valid())
            sys.stdout.flush()
        self.assertEqual(buf.getvalue(), '\n'.join([
            'Validating ' + str(fp_1),
            '  [31m✕ last name should be unique[0m',
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

        file = File(fp.parent, str(fp), schema=Schema('person', columns=[
            {'name': 'age', 'integer': True},
            {'name': 'last', 'unique': True}
        ]), no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            self.assertFalse(file.valid())
            sys.stdout.flush()
        self.assertEqual(buf.getvalue(), '\n'.join([
            'Validating ' + str(fp),
            '[31m  ✕ Does not match schema[0m',
            '    [31m✕[0m column [33mlast[0m failed [35munique[0m check. [36m1[0m offending values:',
            '      0    smith',
            '',
        ]))
