import pathlib

import pandas as pd
import yaml

from .schema import Schema
from .exceptions import BadConfigError
from .file import File


class Config(object):
    """Configures everything that datavalid does

    This is the entry point of datavalid. Config and most classes are designed
    to be instantiated from values read from a YAML file.
    """

    _files: dict[str, File]
    _schemas: dict[str, Schema]

    def __init__(
            self,
            datadir: pathlib.Path,
            files: dict or None = None,
            schemas: dict[str, dict] or None = None,
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
            schemas (list):
                A list of schemas.
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
        self._schemas = dict()
        if save_bad_rows_to is not None:
            if type(save_bad_rows_to) is not str:
                raise BadConfigError(
                    [], 'key "save_bad_rows_to" should be a file path relative to data dir')
        if files is None:
            raise BadConfigError([], 'key "files" should appear at top level')
        if type(files) != dict:
            raise BadConfigError(
                [],
                '"files" should contain a map of file paths and corresponding schema')
        if schemas is None:
            raise BadConfigError(
                [], 'key "schemas" should appear at the top level')
        if type(schemas) != dict:
            raise BadConfigError(
                [],
                '"schemas" should contain a map of schema definitions'
            )
        for name, schema in schemas.items():
            try:
                self._schemas[name] = Schema(
                    name, **schema
                )
            except BadConfigError as e:
                raise BadConfigError(['schemas', name]+e.path, e.msg)
        for name, file_conf in files.items():
            if 'schema' not in file_conf or type(file_conf['schema']) != str:
                raise BadConfigError(
                    ['files', name],
                    '"schema" should be the name of a defined schema in the "schemas" section at the top level'
                )
            try:
                schema_name = file_conf.pop('schema')
                self._files[name] = File(
                    datadir, name, schema=self._schemas[schema_name],
                    save_bad_rows_to=save_bad_rows_to, no_spinner=no_spinner, **file_conf
                )
            except BadConfigError as e:
                raise BadConfigError(['files', name]+e.path, e.msg)

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

    def rearrange_columns(self, schema_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Rearranges and validates columns according to the named schema

        Args:
            schema_name (str):
                name of a defined schema
            df (pd.DataFrame):
                the frame to rearrange

        Returns:
            the rearranged frame
        """
        return self._schemas[schema_name].rearrange_columns(df)

    def to_markdown(self, relative_to: pathlib.Path or None = None) -> str:
        """Render file schemas as markdown"""
        return "\n".join([
            file.to_markdown(relative_to) for file in self._files.values()
        ])


def load_config(datadir: str or pathlib.Path) -> Config:
    if type(datadir) is str:
        datadir = pathlib.Path(datadir)
    conf_file = datadir / 'datavalid.yml'
    if not conf_file.exists():
        raise FileNotFoundError("%s does not exist" % conf_file)
    with conf_file.open() as f:
        obj = yaml.load(f.read(), Loader=yaml.Loader)
    return Config(datadir, **obj)
