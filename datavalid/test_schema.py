from unittest import TestCase

import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from datavalid.schema import FieldSchema


class FieldSchemaTestCase(TestCase):
    def test_validate(self):
        field = FieldSchema(
            "test_field", unique=True, no_na=True, options=['a', 'b', 'c']
        )

        self.assertTrue(field.valid(pd.Series(['b', 'c', 'a'])))

        self.assertFalse(field.valid(pd.Series(['b', 'a', 'b'])))
        assert_series_equal(field.sr, pd.Series(['b', 'b'], index=[0, 2]))
        self.assertEqual(field.failed_check, 'unique')

        self.assertFalse(field.valid(pd.Series(['b', 'a', np.NaN])))
        assert_series_equal(
            field.sr, pd.Series([np.NaN], index=[2]), check_dtype=False
        )
        self.assertEqual(field.failed_check, 'no_na')

        self.assertFalse(field.valid(pd.Series(['d', 'a', 'c'])))
        assert_series_equal(field.sr, pd.Series(['d']))
        self.assertEqual(field.failed_check, 'options')
