from unittest import TestCase

import pandas as pd
from pandas.testing import assert_frame_equal

from datavalid.task import Task


class TaskTestCase(TestCase):
    def test_run(self):
        columns = ['first', 'last', 'age']
        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=columns)

        task = Task('everyone should be older than 25', empty={
                    'column': 'age', 'op': 'greater_than', 'value': 25})
        self.assertFalse(task.run(df))
        self.assertEqual(task.err_msg, 'There are 2 such rows')
        assert_frame_equal(task.df, pd.DataFrame([
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=columns))

        task = Task(
            'the smiths should have unique first name',
            where={'column': 'last', 'op': 'equal', 'value': 'smith'},
            unique='first'
        )
        self.assertTrue(task.run(df))

        task = Task(
            'officer should not have left dates too close together',
            group_by='uid',
            no_more_than_once_a_month={'date_from': {
                'year_column': 'year', 'month_column': 'month', 'day_column': 'day'
            }}
        )
        self.assertTrue(task.run(pd.DataFrame([
            ['john', 2000, 1, 1],
            ['tate', 2000, 1, 1],
            ['cate', 2000, 1, 1],
        ], columns=['uid', 'year', 'month', 'day'])))
