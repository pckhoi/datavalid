from unittest import TestCase

import pandas as pd
from pandas.testing import assert_frame_equal

from datavalid.task import Task
from datavalid.exceptions import TaskValidationError


class TaskTestCase(TestCase):
    def test_run(self):
        columns = ['first', 'last', 'age']
        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=columns)

        task = Task(
            'everyone should be younger than 25',
            empty={
                'column': 'age', 'op': 'greater_equal', 'value': 25
            }
        )
        with self.assertRaises(TaskValidationError) as cm:
            task.run(df)
        self.assertEqual(cm.exception.err_msg, 'There are 2 such rows')
        self.assertEqual(cm.exception.task_name, task.name)
        assert_frame_equal(cm.exception.rows, pd.DataFrame([
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=columns))

        task = Task(
            'the smiths should have unique first name',
            where={'column': 'last', 'op': 'equal', 'value': 'smith'},
            unique='first'
        )
        task.run(df)

        task = Task(
            'officer should not have left dates too close together',
            group_by='uid',
            no_more_than_once_per_30_days={'date_from': {
                'year_column': 'year', 'month_column': 'month', 'day_column': 'day'
            }}
        )
        task.run(pd.DataFrame([
            ['john', 2000, 1, 1],
            ['tate', 2000, 1, 1],
            ['cate', 2000, 1, 1],
        ], columns=['uid', 'year', 'month', 'day']))

        task = Task(
            'birth dates should be valid',
            valid_date={
                'date_from': {
                    'year_column': 'year', 'month_column': 'month', 'day_column': 'day'
                },
                'min_date': '1900-01-01'
            }
        )
        task.run(pd.DataFrame([
            ['john', 1970, 10, 1],
            ['tate', 1960, 2, 28],
            ['cate', 1993, 11, 12],
        ], columns=['uid', 'year', 'month', 'day']))
