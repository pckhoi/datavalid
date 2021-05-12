import pandas as pd

from datavalid.testing import BaseTestCase
from datavalid.group_by import GroupBy


class GroupByTestCase(BaseTestCase):
    def test_groups(self):
        columns = ['first', 'last', 'age']
        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=columns)

        self.assert_frames_equal(
            list(GroupBy(None).groups(df)),
            [
                pd.DataFrame([
                    ['john', 'doe', 23],
                    ['jean', 'smith', 43],
                    ['jane', 'smith', 30]
                ], columns=columns)
            ])

        self.assert_frames_equal(
            list(GroupBy('last').groups(df)),
            [
                pd.DataFrame([
                    ['john', 'doe', 23],
                ], columns=columns),
                pd.DataFrame([
                    ['jean', 'smith', 43],
                    ['jane', 'smith', 30]
                ], index=[1, 2], columns=columns)
            ])

        self.assert_frames_equal(
            list(GroupBy(['first', 'last']).groups(df)),
            [
                pd.DataFrame([
                    ['jane', 'smith', 30]
                ], index=[2], columns=columns),
                pd.DataFrame([
                    ['jean', 'smith', 43],
                ], index=[1], columns=columns),
                pd.DataFrame([
                    ['john', 'doe', 23],
                ], columns=columns),
            ])
