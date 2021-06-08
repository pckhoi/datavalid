import pathlib

import pandas as pd

from .exceptions import BadConfigError
from .file import File


class Config(object):
    """Configures everything that datavalid does

    This is the entry point of datavalid. Config and most classes are designed
    to be instantiated from values read from a YAML file.
    """

    _files: dict[str, File]

    def __init__(
            self,
            datadir: pathlib.Path,
            files: dict or None = None,
            save_bad_rows_to: str or None = None,
            no_spinner: bool = False) -> None:
        """Creates new instance of Config.

        Args:
            datadir (pathlib.Path):
                directory path which contain all data. All file paths in `files` will
                be interpreted based on this directory.
            files (dict):
                A dictionary each key is a path to data file (must be in CSV format),
                each value is a dictionary that can be unpacked as keyword arguments to
                create `File` objects.
            save_bad_rows_to (str):
                A path point to where offending rows should be saved. If this is not
                specified then the rows will just be output to screen
            no_spinner (bool):
                If set to True then don't show spinner on terminal when processing.
                This is mostly useful during unit tests.

        Raises:
            BadConfigError: There's a problem with passed-in arguments

        Returns:
            no value
        """
        self._datadir = datadir
        self._files = dict()
        if save_bad_rows_to is not None:
            if type(save_bad_rows_to) is not str:
                raise BadConfigError(
                    [], 'key "save_bad_rows_to" should be a file path relative to data dir')
        if files is None:
            raise BadConfigError([], 'key "files" should appear at top level')
        if type(files) != dict:
            raise BadConfigError(
                [],
                '"files" should contain a map of file paths and validation steps for each of them')
        for name, file_conf in files.items():
            self._files[name] = File(
                datadir, name, save_bad_rows_to=save_bad_rows_to, no_spinner=no_spinner, **file_conf
            )

    def run(self) -> int:
        """Run all validation tasks and print result to terminal.

        Returns:
            The exit code for the program.
        """
        succeed = True
        for file in self._files.values():
            if not file.valid():
                succeed = False
        if not succeed:
            return 1
        print("All good!")
        return 0

    def to_markdown(self, relative_to: pathlib.Path or None = None) -> str:
        """Render file schemas as markdown"""
        return "\n".join([
            file.to_markdown(relative_to) for file in self._files.values()
        ])
