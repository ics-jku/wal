'''Main wawk command line tool entry point'''
import argparse
import os
import sys

from wal.core import Wal
from wal.util import wal_str
from .parser import parse_wawk
from .ast_defs import AST

__version__ = '0.2'

class Arguments:  # pylint: disable=too-few-public-methods
    '''Wrapper class for argument parser'''

    def __init__(self):
        parser = argparse.ArgumentParser()
        self.parser = parser

        parser.add_argument('program_path', help='path to WAWK file')
        parser.add_argument('trace', help='path to trace file')
        parser.add_argument('args', nargs='*',
                            default=None, help='runtime arguments')
        parser.add_argument('-v', '--version', action='version',
                            version=f'%(prog)s {__version__}')
        parser.add_argument('-o', '--output', nargs='?', default=None, help='Do not run but only write WAL program to file.')

    def parse(self):
        '''Parse program arguments and check minimal requirements'''
        args = self.parser.parse_args()

        return args


def run():
    '''Entry point for the application script'''

    arg_parser = Arguments()
    args = arg_parser.parse()
    sys.setrecursionlimit(5000)

    try:
        with open(args.program_path, 'r', encoding='UTF-8') as program_file:
            ast = AST(parse_wawk(program_file.read()), args.trace)
    except FileNotFoundError as exception:
        print(exception)
        return os.EX_NOINPUT
    except IOError as exception:
        print(exception)
        return os.EX_IOERR

    wal = Wal()
    wal.eval_context.global_environment.write('args', args.args)

    if args.output:
        with open(args.output, 'w') as f:
            stmts, symbols = ast.emit()
            for stmt in stmts:
                f.write(wal_str(stmt) + '\n\n')
    else:
        exprs, symbols = ast.emit()
        wal.load(args.trace, 'WAWK_TRACE', keep_signals=symbols)
        for expr in exprs:
            wal.eval(expr)

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(run())
