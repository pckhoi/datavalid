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
            str(fp_1): {
                'validation_tasks': [
                    {
                        'name': 'the smiths should have unique first name',
                        'where': {'column': 'last', 'op': 'equal', 'value': 'smith'},
                        'unique': 'first'
                    }
                ],
            },
            str(fp_2): {
                'schema': {
                    'event_year': {
                        'integer': True,
                        'range': [2000, 2020]
                    }
                }
            }
        }, no_spinner=True)

        buf = StringIO()
        with redirect_stdout(buf):
            conf.run()
            sys.stdout.flush()
        self.assertEqual(buf.getvalue(), '\n'.join([
            'Validating file ' + str(fp_1),
            '[32m  ✓ the smiths should have unique first name[0m',
            'Validating file ' + str(fp_2),
            '[32m  ✓ Match schema[0m',
            'All good!',
            '',
        ]))

        os.remove(fp_1)
        os.remove(fp_2)
