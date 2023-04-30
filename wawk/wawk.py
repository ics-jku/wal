'''Main wawk command line tool entry point'''
import argparse
import os
import sys

from wal.core import Wal
from wal.ast_defs import Symbol
from .parser import parse_wawk
from .ast_defs import AST

__version__ = '0.2'

class Arguments:  # pylint: disable=too-few-public-methods
    '''Wrapper class for argument parser'''

    def __init__(self):
        parser = argparse.ArgumentParser()
        self.parser = parser

        parser.add_argument('program_path', help='path to vcd file')
        parser.add_argument('vcd', help='path to vcd file')
        parser.add_argument('args', nargs='*',
                            default=None, help='runtime arguments')
        parser.add_argument('-v', '--version', action='version',
                            version=f'%(prog)s {__version__}')

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
    else:
        defined_at = seval.environment.is_defined(key.name)

    if defined_at:
        defined_at.environment[key.name] = res
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
            ast = AST(parse_wawk(program_file.read()))
    except FileNotFoundError as exception:
        print(exception)
        return os.EX_NOINPUT
    except IOError as exception:
        print(exception)
        return os.EX_IOERR

    wal = Wal()
    wal.register_operator('wawk-set', wawk_set)
    wal.eval_context.global_environment.write('args', args.args)
    wal.load(args.vcd, 'main')


    for begin_action in ast.begin:
        wal.eval(begin_action)

    while not wal.step():
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
