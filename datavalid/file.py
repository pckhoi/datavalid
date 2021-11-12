import pathlib
import traceback
import sys
from contextlib import contextmanager
from typing import Iterator

import pandas as pd
from termcolor import colored

from datavalid.exceptions import TaskValidationError

from .utils import indent, TERM_COLS
from .schema import Schema
from .spinner import Spinner
from .task import Task


class File(object):
    """Describes a file and validates it
    """
    _tasks: list[Task]
    _datadir: pathlib.Path
    _filepath: pathlib.Path
    _schema: Schema
    _fields: list[str]
    _save_bad_rows_to: str or None

    def __init__(
        self,
        datadir: pathlib.Path,
        filename: str,
        schema: Schema,
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
        self._schema = schema
        self._tasks = []

    def _col_err_msg(self, col: str, err_msg: str) -> str:
        return indent("%s column %s %s" % (
            colored("✕", "red"), colored(col, "yellow"), err_msg
        ), 4)

    @contextmanager
    def _spinner(self, name: str, indent: int):
        if self._no_spinner:
            yield
        else:
            with Spinner(name, indent=indent) as spinner:
                yield spinner

    def _validate_schema(self, df: pd.DataFrame) -> Iterator[str]:
        for err in self._schema.column_errors(df):
            yield self._col_err_msg(err.column, err.msg)

    def _validate_tasks(self, df: pd.DataFrame) -> bool:
        for task in self._schema.tasks:
            with self._spinner(task.name, indent=2):
                try:
                    task.run(df)
                except TaskValidationError as err:
                    if err.warn:
                        print(indent(colored("⚠ %s" % task.name, "yellow"), 2))
                    else:
                        print(indent(colored("✕ %s" % task.name, "red"), 2))
                    print(indent(err.err_msg, 4))
                    if not err.warn and self._save_bad_rows_to is not None:
                        rows_path = self._datadir / self._save_bad_rows_to
                        err.rows.to_csv(rows_path, index=False)
                        print(indent('Saved bad rows to %s' % rows_path, 4))
                    else:
                        print(indent(err.rows.to_string(
                            line_width=TERM_COLS-4), 4))
                    if not err.warn:
                        return False
                except Exception:
                    print(indent(colored("✕ %s" % task.name, "red"), 2))
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    print(indent(
                        'an error occured during task execution: %s' % ''.join(traceback.format_exception_only(
                            exc_type, exc_value
                        )).strip(),
                        4
                    ))
                    for line in traceback.format_tb(exc_tb):
                        print(indent(line.strip(), 6))
                    return False
                else:
                    print(indent(colored("✓ %s" % task.name, "green"), 2))
        return True

    def valid(self) -> bool:
        """Checks whether this file pass all validation tasks and match schema
        """
        print("Validating %s" % self._filepath)
        df = pd.read_csv(self._filepath, low_memory=False)
        succeed = True

        if len(self._schema.columns) > 0:
            msgs = []
            with self._spinner('Validating columns', indent=2) as spinner:
                for err_msg in self._validate_schema(df):
                    msgs.append(err_msg)
                if spinner is not None:
                    spinner.set_postfix_text('\n'.join(msgs))
            if len(msgs) == 0:
                print(colored("  ✓ All columns match schema", "green"))
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
            "- schema: [%s](#schema-%s)" % (
                self._schema.name,
                self._schema.name.lower().replace(' ', '-')
            )
        ])
