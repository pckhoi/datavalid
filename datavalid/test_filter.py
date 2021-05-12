import pandas as pd

from datavalid.testing import BaseTestCase
from datavalid.filter import Filter


class FilterTestCase(BaseTestCase):
    def test_filter(self):
        columns = ['first', 'last', 'age']
        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=columns)

        self.assert_frames_equal(
            list(Filter().filter(df)),
            [df]
        )

        self.assert_frames_equal(
            list(Filter(
                {'column': 'last', 'op': 'equal', 'value': 'smith'},
                'first'
            ).filter(df)),
            [
                pd.DataFrame([
                    ['jane', 'smith', 30]
                ], index=[1], columns=columns),
                pd.DataFrame([
                    ['jean', 'smith', 43],
                ], index=[0], columns=columns)
            ]
        )
