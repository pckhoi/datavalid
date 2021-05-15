import pathlib

import pandas as pd
from termcolor import colored

from .task import Task
from .spinner import Spinner


class Config(object):
    def __init__(self, datadir: pathlib.Path, files: dict) -> None:
        self._datadir = datadir
        self._files = dict()
        for name, objs in files.items():
            self._files[name] = []
            for obj in objs:
                self._files[name].append(Task(**obj))

    def run(self) -> None:
        for name, tasks in self._files.items():
            print("File %s" % name)
            filepath = self._datadir / name
            df = pd.read_csv(filepath)
            for task in tasks:
                with Spinner(task.name, indent=2):
                    succeed = task.run(df)
                if succeed:
                    print("  %s %s" % (colored("✓", "green"), task.name))
                else:
                    print("  %s %s" % (colored("✕", "red"), task.name))
                    print(' '*4+task.err_msg.replace('\n', '\n    '))
                    return
        print("All good!")
