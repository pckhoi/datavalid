import pathlib

import pandas as pd
from termcolor import colored

from .exceptions import BadConfigError
from .schema import FieldSchema
from .spinner import Spinner
from .task import Task


class File(object):
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
        schema: dict,
        validation_tasks: list[dict] or None = None,
        save_bad_rows_to: str or None = None,
        no_spinner: bool = False
    ) -> None:
        self._datadir = datadir
        self._filepath = self._datadir / filename
        self._no_spinner = no_spinner
        self._save_bad_rows_to = save_bad_rows_to
        self._schema = dict()
        self._fields = list()
        for k, v in schema.items():
            self._fields.append(k)
            if v is None:
                continue
            if type(v) is not dict:
                raise BadConfigError(
                    ['schema', k], 'value must be a dictionary'
                )
            self._schema[k] = FieldSchema(**v)

        if type(validation_tasks) != list:
            raise BadConfigError(
                ['validation_tasks'],
                'should be a list of validation tasks')
        self._tasks = []
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

    def print_col_err(self, col: str, err_msg: str) -> None:
        print("  %s column \"%s\" %s" % (
            colored("✕", "red"), col, err_msg
        ))

    def valid(self) -> bool:
        print("Validating file %s" % self._filepath)
        df = pd.read_csv(self._filepath, low_memory=False)

        for col, schema in self._schema.items():
            if col not in df.columns:
                self.print_col_err(col, "is not present")
                return False
            if not schema.validate(df[col]):
                self.print_col_err(col, "failed %s check. Offending values:\n    %s" % (
                    schema.failed_check, schema.sr.to_string().replace('\n', '\n    ')
                ))

        for task in self._tasks:
            if self._no_spinner:
                succeed = task.run(df)
            else:
                with Spinner(task.name, indent=2):
                    succeed = task.run(df)
            if succeed:
                print("  %s %s" % (colored("✓", "green"), task.name))
            else:
                print("  %s %s" % (colored("✕", "red"), task.name))
                print(' '*4+task.err_msg.replace('\n', '\n    '))
                if self._save_bad_rows_to is not None:
                    rows_path = self._datadir / self._save_bad_rows_to
                    task.df.to_csv(rows_path, index=False)
                    print('    Saved bad rows to %s' % rows_path)
                else:
                    print(' '*4+task.df.to_string().replace('\n', '\n    '))
                return False

        return True
