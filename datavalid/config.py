import pathlib

import pandas as pd
from termcolor import colored

from .task import Task
from .spinner import Spinner
from .exceptions import BadConfigError


class Config(object):
    def __init__(self, datadir: pathlib.Path, files: dict or None = None, save_bad_rows_to: str or None = None, no_spinner: bool = False) -> None:
        self._datadir = datadir
        self._files = dict()
        self._no_spinner = no_spinner
        if save_bad_rows_to is not None:
            if type(save_bad_rows_to) is not str:
                raise BadConfigError(
                    [], 'key "save_bad_rows_to" should be a file path relative to data dir')
        self._save_bad_rows_to = save_bad_rows_to
        if files is None:
            raise BadConfigError([], 'key "files" should appear at top level')
        if type(files) != dict:
            raise BadConfigError(
                [],
                '"files" should contain a map of file paths and validation steps for each of them')
        for name, tasks in files.items():
            self._files[name] = []
            if type(tasks) != list:
                raise BadConfigError(
                    ['files', name],
                    'should be a list of validation tasks')
            for i, task in enumerate(tasks):
                try:
                    self._files[name].append(Task(**task))
                except (BadConfigError, TypeError) as e:
                    raise BadConfigError(
                        [],
                        'error creating task %d for file %s:\n  %s' % (
                            i, name, str(e).replace('\n', '\n  '))
                    )

    def run(self) -> int:
        for name, tasks in self._files.items():
            filepath = self._datadir / name
            print("Validating file %s" % filepath)
            df = pd.read_csv(filepath, low_memory=False)
            for task in tasks:
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
                    return 1
        print("All good!")
        return 0
