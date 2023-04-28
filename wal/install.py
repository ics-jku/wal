'''Installation routine, creates a .wal dir if none exists and copies the stdlib into .wal '''
import os

try:
    from importlib.resources import files
except ImportError:
    # for python < 3.9
    from importlib_resources import files


import wal

def compile_stdlib(wal_obj):
    'compile wal std lib file'
    wal_path = files(wal).joinpath('libs/std/std.wal')
    wo_path = files(wal).joinpath('libs/std/std.wo')

    from wal.walc import wal_compile # pylint: disable=C0415

    if not os.path.isfile(wo_path):
        print('Preparing stdlib...', end=' ', flush = True)
        wal_compile(wal_path, wo_path, wal=wal_obj)
        print('🐳')
