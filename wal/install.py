import os
import wal
from importlib.resources import files
from distutils.dir_util import copy_tree
from wal.walc import wal_compile

def run():
    wal_path = os.path.expanduser('~/.wal')
    wal_libs = wal_path + '/libs'

    if not os.path.exists(wal_path):
        os.mkdir(wal_path)
        os.mkdir(wal_libs)

    copy_tree(files(wal).joinpath('libs/std'), wal_libs)

    # compile wal std lib file
    wal_compile(wal_libs + '/std.wal', wal_libs + '/std.wo')
