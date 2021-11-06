'''Main wal command line tool entry point'''
import argparse
import os
import sys

from wal.core import Wal
from .parser import parse_wawk
from .ast_defs import AST

__version__ = '0.2'

class Arguments:  # pylint: disable=too-few-public-methods
    '''Wrapper class for argument parser'''

    def __init__(self):
        parser = argparse.ArgumentParser()
        self.parser = parser

        parser.add_argument('program', nargs='?',
                            default=None, help='program code')
        parser.add_argument('vcd', help='path to vcd file')
        parser.add_argument('-f', action='store', dest='program_path',
                            help='path to wal program file')
        parser.add_argument('-v', '--version', action='version',
                            version=f'%(prog)s {__version__}')

    def parse(self):
        '''Parse program arguments and check minimal requirements'''
        args = self.parser.parse_args()

        if args.program is None:
            if args.program_path is None:
                return None
        return args


def run():
    '''Entry point for the application script'''

    arg_parser = Arguments()
    args = arg_parser.parse()
    sys.setrecursionlimit(5000)

    if args.program:
        p = parse_wawk(args.program)
        # print(p)
        ast = AST(parse_wawk(args.program))
        # ast = AST(program.parse(args.program))
    else:
        try:
            with open(args.program_path, 'r') as program_file:
                ast = AST(parse_wawk(program_file.read()))
        except FileNotFoundError as exception:
            print(exception)
            return os.EX_NOINPUT
        except IOError as exception:
            print(exception)
            return os.EX_IOERR

    wal = Wal()
    wal.load(args.vcd, 'main')

    for begin_action in ast.begin:
        wal.eval(begin_action)
        
    while wal.step() == []:
        for statement in ast.statements:
            conditions = []
            for cond in statement.condition:
                try:
                    eval_cond = wal.eval(cond)
                except Exception as e: # pylint: disable=W0703,C0103
                    print('ERROR|', e, '\n', cond)
                    sys.exit()
                conditions.append(eval_cond)

            if all(conditions):
                wal.eval(statement.action)

    for end_action in ast.end:
        wal.eval(end_action)

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(run())
