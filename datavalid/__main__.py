import argparse
import pathlib
import sys

import yaml

from .config import Config
from .exceptions import BadConfigError

parser = argparse.ArgumentParser(
    prog='datavalid', description='validate CSV files')
parser.add_argument(
    "--dir", help="directory that contain datavalid.yml", type=pathlib.Path
)
parser.add_argument(
    "--doc", help="output markdown documentation to this file", type=pathlib.Path
)
args = parser.parse_args()
if args.dir is None:
    datadir = pathlib.Path.cwd()
elif not args.dir.exists() or not args.dir.is_dir():
    sys.exit("%s is not a valid directory" % args.dir)
else:
    datadir = args.dir
conf_file = datadir / 'datavalid.yml'
if not conf_file.exists():
    sys.exit("%s does not exist" % conf_file)
with conf_file.open() as f:
    obj = yaml.load(f.read(), Loader=yaml.Loader)
try:
    conf = Config(datadir, **obj)
except BadConfigError as e:
    print("Error parsing config file %s:\n  %s" %
          (str(conf_file), str(e).replace('\n', '\n  ')))
    sys.exit(1)
if args.doc:
    with open(args.doc, 'w') as f:
        f.write(conf.to_markdown(args.doc.parent).strip()+'\n')
else:
    sys.exit(conf.run())
