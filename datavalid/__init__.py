import argparse
import pathlib
import sys

import yaml

from .config import Config
from .exceptions import BadConfigError

__all__ = ["Config"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir", help="directory that contain datavalid.yml", type=pathlib.Path)
    args = parser.parse_args()
    if args.dir is None:
        datadir = pathlib.Path.cwd()
    elif not args.dir.exists() or not args.is_dir():
        sys.exit("%s is not a valid directory" % args.dir)
    else:
        datadir = args.dir
    conf_file = datadir / 'datavalid.yml'
    if not conf_file.exists():
        sys.exit("%s does not exist" % conf_file)
    with conf_file.open() as f:
        obj = yaml.load(f.read())
    try:
        conf = Config(datadir, **obj)
    except BadConfigError as e:
        print("Error parsing config file %s:\n  %s" %
              (str(conf_file), e.args[0].replace('\n', '\n  ')))
        sys.exit(1)
    sys.exit(conf.run())
