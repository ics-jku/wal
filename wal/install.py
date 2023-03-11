'''Installation routine, creates a .wal dir if none exists and copies the stdlib into .wal '''
import os
import shutil
from importlib.resources import files

import wal
from wal.walc import wal_compile

def run():
    '''Entry point for wal_setup script'''
    wal_path = os.path.expanduser('~/.wal')
    wal_libs = wal_path + '/libs'

    if not os.path.exists(wal_path):
        os.mkdir(wal_path)
        os.mkdir(wal_libs)

    shutil.copytree(files(wal).joinpath('libs/std'), wal_libs, dirs_exist_ok=True)

    # compile wal std lib file
    wal_compile(wal_libs + '/std.wal', wal_libs + '/std.wo')
