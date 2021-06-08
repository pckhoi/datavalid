import os
import pathlib
from contextlib import contextmanager
from typing import Iterator

import pandas as pd
from termcolor import colored

from .exceptions import BadConfigError
from .schema import FieldSchema
from .spinner import Spinner
from .task import Task

try:
    TERM_COLS = int(os.popen('stty size', 'r').read().split()[1])
except IndexError:
    TERM_COLS = 100


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
                try:
                    self._schema[k] = FieldSchema(k, **v)
                except BadConfigError as e:
                    raise BadConfigError(
                        ['schema', k]+e.path, e.msg
                    )
                except TypeError as e:
                    raise BadConfigError(
                        ['schema', k], str(e)
                    )

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

    def _col_err_msg(self, col: str, err_msg: str) -> str:
        return "    %s column %s %s" % (
            colored("✕", "red"), colored(col, "yellow"), err_msg
        )

    @contextmanager
    def _spinner(self, name: str, indent: int):
        if self._no_spinner:
            yield
        else:
            with Spinner(name, indent=indent) as spinner:
                yield spinner

    def _validate_schema(self, df: pd.DataFrame) -> Iterator[str]:
        for col, schema in self._schema.items():
            if col not in df.columns:
                yield self._col_err_msg(col, "is not present")
            elif not schema.valid(df.loc[:, col]):
                if schema.sr.size > 10:
                    sr = schema.sr[:10]
                    dots = '\n      ...'
                else:
                    sr = schema.sr
                    dots = ''
                yield self._col_err_msg(
                    col,
                    'failed %s check. %s offending values:\n      %s%s' % (
                        colored(schema.failed_check, "magenta"),
                        colored(schema.sr.size, "cyan"),
                        sr.to_string().replace('\n', '\n      '),
                        dots
                    )
                )

    def _validate_tasks(self, df: pd.DataFrame) -> bool:
        for task in self._tasks:
            with self._spinner(task.name, indent=2):
                succeed = task.run(df)
            if succeed:
                print(colored("  ✓ %s" % task.name, "green"))
            else:
                if task.warn_only:
                    print(colored("  ⚠ %s" % task.name, "yellow"))
                else:
                    print(colored("  ✕ %s" % task.name, "red"))
                print(' '*4+task.err_msg.replace('\n', '\n    '))
                if not task.warn_only and self._save_bad_rows_to is not None:
                    rows_path = self._datadir / self._save_bad_rows_to
                    task.df.to_csv(rows_path, index=False)
                    print('    Saved bad rows to %s' % rows_path)
                else:
                    print(
                        ' '*4 +
                        task.df.to_string(line_width=TERM_COLS-4)
                        .replace('\n', '\n    ')
                    )
                if not task.warn_only:
                    return False
        return True

    def valid(self) -> bool:
        """Checks whether this file pass all validation tasks and match schema
        """
        print("Validating file %s" % self._filepath)
        df = pd.read_csv(self._filepath, low_memory=False)
        succeed = True

        if len(self._schema) > 0:
            msgs = []
            with self._spinner('Validating schema', indent=2) as spinner:
                for err_msg in self._validate_schema(df):
                    msgs.append(err_msg)
                if spinner is not None:
                    spinner.set_postfix_text('\n'.join(msgs))
            if len(msgs) == 0:
                print(colored("  ✓ Match schema", "green"))
            else:
                succeed = False
                print(colored("  ✕ Does not match schema", "red"))
                for err_msg in msgs:
                    print(err_msg)

        if not self._validate_tasks(df):
            return False

        return succeed

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
                ]+[""]
            )
        )
        )
