from typing import Iterator

import pandas as pd

from .exceptions import BadConfigError, ColumnMissingError, ColumnValidationError, ColumnError
from .column_schema import ColumnSchema
from .task import Task


class Schema(object):
    """Describes a table and how to validate it.
    """
    columns: dict[str, ColumnSchema]

    def __init__(self, name: str, columns: list[dict] or None = None, validation_tasks: list[dict] or None = None):
        """Creates a new instance of Schema

        Args:
            name (str):
                the name of the schema
            columns (list of dict):
                schema for each column
            validation_tasks (list):
                additional validation tasks to run on this file

        Returns:
            no value
        """
        self.name = name
        self._column_names = list()
        self.columns = dict()
        self.tasks = []
        seen_column_names = set()
        if columns is not None:
            if type(columns) != list:
                raise BadConfigError(
                    ['columns'],
                    'should be a list of columns and their description'
                )
            for idx, obj in enumerate(columns):
                if type(obj) != dict:
                    raise BadConfigError(
                        ['columns', idx],
                        'column schema must be a dictionary'
                    )
                if 'name' not in obj:
                    raise BadConfigError(
                        ['columns', idx, 'name'],
                        'each column must have field "name"'
                    )
                if obj['name'] in seen_column_names:
                    raise BadConfigError(
                        ['columns', idx, 'name'],
                        'repeating column name'
                    )
                seen_column_names.add(obj['name'])
                self._column_names.append(obj['name'])
                try:
                    self.columns[obj['name']] = ColumnSchema(**obj)
                except BadConfigError as e:
                    raise BadConfigError(
                        ['columns', idx]+e.path, e.msg
                    )
                except TypeError as e:
                    raise BadConfigError(
                        ['columns', idx], str(e)
                    )

        if validation_tasks is not None:
            if type(validation_tasks) != list:
                raise BadConfigError(
                    ['validation_tasks'],
                    'should be a list of validation tasks')
            for i, task in enumerate(validation_tasks):
                try:
                    self.tasks.append(Task(**task))
                except BadConfigError as e:
                    raise BadConfigError(
                        ['validation_tasks', i]+e.path, e.msg
                    )
                except TypeError as e:
                    raise BadConfigError(
                        ['validation_tasks', i], str(e)
                    )

    def column_errors(self, df: pd.DataFrame) -> Iterator[ColumnError]:
        """Validates and returns column errors as a generator.

        If this doesn't yield anything, that means the frame matches the schema.

        Args:
            df (pd.DataFrame):
                the frame to validate

        Returns:
            a generator that yield ColumnError
        """
        for col, col_schema in self.columns.items():
            if col not in df.columns:
                yield ColumnMissingError(col)
            else:
                try:
                    col_schema.validate(df.loc[:, col])
                except ColumnValidationError as e:
                    yield e

    def rearrange_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rearranges columns according to the order in the schema and checks against the column schemas.

        Args:
            df (pd.DataFrame):
                the frame to rearrange

        Returns:
            the rearranged frame
        """
        existing_cols = set(df.columns)
        df = df[[col for col in self._column_names if col in existing_cols]]\
            .drop_duplicates(ignore_index=True)
        for col, col_schema in self.columns.items():
            if col in existing_cols:
                col_schema.validate(df.loc[:, col])
        return df

    def to_markdown(self) -> str:
        """Render this schema as Markdown

        Returns:
            markdown string
        """
        return "\n".join([
            "## Schema %s" % self.name,
            "",
        ]+(
            [] if len(self.columns) == 0 else (
                [
                    "### columns",
                    ""
                ]+[
                    field.to_markdown() for field in self.columns.values()
                ]
            )
        )+(
            [] if len(self._tasks) == 0 else (
                [
                    "### Validation tasks",
                    ""
                ]+[
                    task.to_markdown() for task in self._tasks
                ]+[""]
            )
        )
        )
