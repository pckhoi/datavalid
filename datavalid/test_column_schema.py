from unittest import TestCase

import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from datavalid.column_schema import ColumnSchema
from datavalid.exceptions import ColumnValidationError


class ColumnSchemaTestCase(TestCase):
    def test_validate(self):
        field = ColumnSchema(
            "test_field", unique=True, no_na=True, options=['a', 'b', 'c']
        )

        field.validate(pd.Series(['b', 'c', 'a']))

        with self.assertRaises(ColumnValidationError) as cm:
            field.validate(pd.Series(['b', 'a', 'b']))
        assert_series_equal(
            cm.exception.values, pd.Series(['b']))
        self.assertEqual(cm.exception.failed_check, 'unique')

        with self.assertRaises(ColumnValidationError) as cm:
            field.validate(pd.Series(['b', 'a', np.NaN]))
        assert_series_equal(
            cm.exception.values, pd.Series([np.NaN]), check_dtype=False
        )
        self.assertEqual(cm.exception.failed_check, 'no_na')

        with self.assertRaises(ColumnValidationError) as cm:
            field.validate(pd.Series(['d', 'a', 'c']))
        assert_series_equal(cm.exception.values, pd.Series(['d']))
        self.assertEqual(cm.exception.failed_check, 'options')
