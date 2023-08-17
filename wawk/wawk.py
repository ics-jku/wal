'''Main wawk command line tool entry point'''
import argparse
import os
import sys

from wal.core import Wal
from wal.ast_defs import Symbol
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


def wawk_set(seval, args):
    '''This is basically WAL's set implementation but undefined signals get defined'''
    key = args[0]
    assert isinstance(key, Symbol), 'assertion key must be a symbol'
    res = seval.eval(args[1])

    # this signal was already resolved
    if key.steps is not None:
        defined_at = seval.environment
        steps = key.steps
        while steps > 0:
            defined_at = seval.environment.parent
            steps -= 1

        # get the dict out of the environment
        defined_at = defined_at.environment
    else:
        defined_at = seval.environment.is_defined(key.name)

    if defined_at:
        defined_at[key.name] = res
    else:
        assert f'Write to undefined symbol {key.name}'
        seval.environment.define(key.name, res)
    
    return res

    
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
    wal.register_operator('wawk-set', wawk_set)
    wal.eval_context.global_environment.write('args', args.args)
    #wal.load(args.trace, 'main')

    if args.output:
        with open(args.output, 'w') as f:
            for stmt in ast.emit():
                f.write(wal_str(stmt) + '\n\n')
    else:
        exprs, symbols = ast.emit()
        wal.load(args.trace, 'WAWK_TRACE', keep_signals=symbols)
        print("a")
        for expr in exprs:
            wal.eval(expr)

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(run())
