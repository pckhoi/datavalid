from unittest import TestCase
from dataclasses import dataclass, asdict, field
from typing import List

import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal

from datavalid.condition import Condition


class ConditionTestCase(TestCase):
    def test_bool_index(self):
        @dataclass
        class Case:
            result: pd.Series
            column: str or None = field(default=None)
            op: str or None = field(default=None)
            value: str or int or None = field(default=None)
            together: List or None = field(default=None)
            either_or: List or None = field(default=None)

        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=['first', 'last', 'age'])

        cases = [
            Case(result=pd.Series([True, True, True])),
            Case(column='first', op='equal', value='john',
                 result=pd.Series([True, False, False])),
            Case(column='first', op='not_equal', value='john',
                 result=pd.Series([False, True, True])),
            Case(column='age', op='greater_than', value=30,
                 result=pd.Series([False, True, False])),
            Case(column='age', op='less_than', value=30,
                 result=pd.Series([True, False, False])),
            Case(column='age', op='greater_equal', value=30,
                 result=pd.Series([False, True, True])),
            Case(column='age', op='less_equal', value=30,
                 result=pd.Series([True, False, True])),
            Case(together=[
                {'column': 'last', 'op': 'equal', 'value': 'smith'},
                {'column': 'age', 'op': 'less_than', 'value': 40}
            ], result=pd.Series([False, False, True])),
            Case(either_or=[
                {'column': 'last', 'op': 'equal', 'value': 'smith'},
                {'column': 'age', 'op': 'less_than', 'value': 30}
            ], result=pd.Series([True, True, True])),
        ]
        for i, case in enumerate(cases):
            cond = Condition(**{
                k: v for k, v in asdict(case).items()
                if k != 'result'
            })
            assert_series_equal(cond.bool_index(
                df), case.result, check_names=False)

    def test_apply(self):
        df = pd.DataFrame([
            ['john', 'doe', 23],
            ['jean', 'smith', 43],
            ['jane', 'smith', 30]
        ], columns=['first', 'last', 'age'])
        cond = Condition(column='first', op='equal', value='john')
        assert_frame_equal(cond.apply(df), pd.DataFrame([
            ['john', 'doe', 23],
        ], columns=['first', 'last', 'age']))
