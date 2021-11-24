from unittest import TestCase

import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal

from datavalid.exceptions import BadConfigError, ColumnMissingError, ColumnValidationError
from datavalid.schema import Schema


class SchemaTestCase(TestCase):
    def test_validate_columns(self):
        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=['first', 'last', 'age'])

        schema = Schema('person', columns=[
            {'name': 'age', 'integer': True},
            {'name': 'last', 'unique': True},
            {'name': 'gender', 'options': ['male', 'female']}
        ])

        errs = list(schema.column_errors(df))
        self.assertEqual(len(errs), 2)
        self.assertIsInstance(errs[0], ColumnValidationError)
        self.assertEqual(errs[0].column, 'last')
        self.assertEqual(errs[0].failed_check, 'unique')
        assert_series_equal(errs[0].values, pd.Series(['smith'], name='last'))
        self.assertIsInstance(errs[1], ColumnMissingError)
        self.assertEqual(errs[1].column, 'gender')

    def test_rearrange_columns(self):
        schema = Schema(
            'person',
            columns=[
                {'name': 'first'},
                {'name': 'last'},
                {'name': 'gender', 'options': ['male', 'female']},
                {'name': 'age', 'integer': True},
            ],
        )

        with self.assertRaises(ColumnValidationError) as cm:
            schema.rearrange_columns(pd.DataFrame([
                ['john', 'doe', 23],
                ['jean', 'smith', 'abc'],
            ], columns=['first', 'last', 'age']))
        self.assertEqual(cm.exception.column, 'age')

        assert_frame_equal(
            schema.rearrange_columns(pd.DataFrame([
                ['jean', 43, 'female'],
                ['paul', 33, 'male'],
            ], columns=['first', 'age', 'gender'])),
            pd.DataFrame([
                ['jean', 'female', 43],
                ['paul', 'male', 33],
            ], columns=['first', 'gender', 'age']),
        )

    def test_duplicated_column_names(self):
        with self.assertRaises(BadConfigError) as ce:
            Schema(
                'allegation',
                columns=[
                    {'name': 'allegation_uid'},
                    {'name': 'allegation_uid'},
                ]
            )
        self.assertEqual(
            ce.exception.args,
            (['columns', 1, 'name'], 'repeating column "allegation_uid"')
        )
