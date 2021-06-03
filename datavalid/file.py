import pathlib
from contextlib import contextmanager

import pandas as pd
from termcolor import colored

from .exceptions import BadConfigError
from .schema import FieldSchema
from .spinner import Spinner
from .task import Task


class File(object):
    """Describes a file and validates it
    """
    _tasks: list[Task]
    _datadir: pathlib.Path
    _filepath: pathlib.Path
    _schema: dict[str, FieldSchema]
    _fields: list[str]
    _save_bad_rows_to: str or None

    def __init__(
        self,
        datadir: pathlib.Path,
        filename: str,
        schema: dict or None = None,
        validation_tasks: list[dict] or None = None,
        save_bad_rows_to: str or None = None,
        no_spinner: bool = False
    ) -> None:
        """Creates a new instance of File

        Args:
            datadir (pathlib.Path):
                the root folder for all data files
            filename (str):
                the file to validate
            schema (dict):
                schema for each column in this file
            validation_tasks (list):
                additional validation tasks to run on this file
            save_bad_rows_to (str):
                if one of the validation tasks fail then save
                the bad rows into this file instead of outputting
                to screen
            no_spinner (bool):
                don't show spinner during processing. Useful during
                tests

        Returns:
            no value
        """
        self._datadir = datadir
        self._filepath = self._datadir / filename
        self._no_spinner = no_spinner
        self._save_bad_rows_to = save_bad_rows_to
        self._fields = list()
        self._schema = dict()
        self._tasks = []
        if schema is not None:
            if type(schema) != dict:
                raise BadConfigError(
                    ['schema'],
                    'should be a dictionary of columns and their description')
            for k, v in schema.items():
                self._fields.append(k)
                if v is None:
                    continue
                if type(v) is not dict:
                    raise BadConfigError(
                        ['schema', k], 'value must be a dictionary'
                    )
                self._schema[k] = FieldSchema(k, **v)

        if validation_tasks is not None:
            if type(validation_tasks) != list:
                raise BadConfigError(
                    ['validation_tasks'],
                    'should be a list of validation tasks')
            for i, task in enumerate(validation_tasks):
                try:
                    self._tasks.append(Task(**task))
                except BadConfigError as e:
                    raise BadConfigError(
                        ['validation_tasks', i]+e.path, e.msg
                    )
                except TypeError as e:
                    raise BadConfigError(
                        ['validation_tasks', i], str(e)
                    )

    def _print_col_err(self, col: str, err_msg: str) -> None:
        print("  %s column \"%s\" %s" % (
            colored("✕", "red"), col, err_msg
        ))

    @contextmanager
    def _spinner(self, name: str, indent: int):
        if self._no_spinner:
            yield
        else:
            with Spinner(name, indent=indent):
                yield

    def _validate_schema(self, df: pd.DataFrame) -> bool:
        for col, schema in self._schema.items():
            if col not in df.columns:
                self._print_col_err(col, "is not present")
                return False
            if not schema.valid(df[col]):
                self._print_col_err(col, 'failed "%s" check. Offending values:\n    %s' % (
                    schema.failed_check, schema.sr.to_string().replace('\n', '\n    ')
                ))
                return False
        return True

    def _validate_tasks(self, df: pd.DataFrame) -> bool:
        for task in self._tasks:
            with self._spinner(task.name, indent=2):
                succeed = task.run(df)
            if succeed:
                print("  %s %s" % (colored("✓", "green"), task.name))
            else:
                if task.warn_only:
                    print("  %s %s" % (colored("⚠", "yellow"), task.name))
                else:
                    print("  %s %s" % (colored("✕", "red"), task.name))
                print(' '*4+task.err_msg.replace('\n', '\n    '))
                if not task.warn_only and self._save_bad_rows_to is not None:
                    rows_path = self._datadir / self._save_bad_rows_to
                    task.df.to_csv(rows_path, index=False)
                    print('    Saved bad rows to %s' % rows_path)
                else:
                    print(' '*4+task.df.to_string().replace('\n', '\n    '))
                if not task.warn_only:
                    return False
        return True

    def valid(self) -> bool:
        """Checks whether this file pass all validation tasks and match schema
        """
        print("Validating file %s" % self._filepath)
        df = pd.read_csv(self._filepath, low_memory=False)

        if len(self._schema) > 0:
            with self._spinner('Validating schema', indent=2):
                if not self._validate_schema(df):
                    return False
                else:
                    print("  %s %s" % (colored("✓", "green"), 'Match schema'))

        if not self._validate_tasks(df):
            return False

        return True

    def to_markdown(self, relative_to: pathlib.Path or None = None) -> str:
        """Render this file's schema as Markdown

        Args:
            relative_to (pathlib.Path):
                file path will be relative to this path. If this is not
                set then file path will be relative to CWD.

        Returns:
            markdown string
        """
        if relative_to is None:
            relative_to = pathlib.Path.cwd()
        return "\n".join([
            "## File %s" % self._filepath.relative_to(relative_to),
            "",
        ]+(
            [] if len(self._schema) == 0 else (
                [
                    "### Schema",
                    ""
                ]+[
                    field.to_markdown() for field in self._schema.values()
                ]
            )
        )+(
            [] if len(self._tasks) == 0 else (
                [
                    "### Other characteristics",
                    ""
                ]+[
                    task.to_markdown() for task in self._tasks
                ]
            )
        )
        )
