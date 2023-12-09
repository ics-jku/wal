'''Main wal command line tool entry point'''
# pylint: disable=C0103,R0912

import argparse
import os
import sys

from wal.core import Wal
from wal.repl import WalRepl
from wal.util import wal_decode
from wal.reader import read_wal_sexprs, ParseError
from wal.passes import expand, optimize, resolve
from wal.version import __version__ as wal_version
from wal.ast_defs import WalEvalError


class Arguments:  # pylint: disable=too-few-public-methods
    '''Wrapper class for argument parser'''

    def __init__(self):
        parser = argparse.ArgumentParser()
        self.parser = parser

        parser.add_argument('-l', '--load', nargs='*', help='paths to waveforms to load')
        parser.add_argument('-c', nargs='?', help='WAL expression to execute')
        parser.add_argument('program_path', nargs='?', help='path to wal/wo file')
        parser.add_argument('-v', '--version', action='version',
                            version=f'%(prog)s {wal_version}')
        parser.add_argument('--repl-on-failure', action='store_true', help='open REPL when a failure occurs')
        parser.add_argument('args', nargs='*',
                            default=None, help='runtime arguments')


    def parse(self):
        '''Parse program arguments and check minimal requirements'''
        args = self.parser.parse_args()

        return args


def run():
    '''Entry point for the application script'''
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit()


def main():  # pylint: disable=R1710
    '''WAL main function'''
    sys.setrecursionlimit(10000)

    arg_parser = Arguments()
    args = arg_parser.parse()

    wal = Wal()
    wal.eval_context.global_environment.write('args', args.args)

    if args.load is not None:
        for i, path in enumerate(args.load):
            wal.load(path, f't{i}')

    if args.c:
        try:
            wal.eval(args.c)
        except Exception as e: # pylint: disable=W0703
            print()
            print('>>>>> Runtime error! <<<<<')
            print(e)
            if args.repl_on_failure:
                WalRepl(wal, intro=WalRepl.dyn_intro).cmdloop()

            return os.EX_SOFTWARE
    else:
        if not args.program_path: # if no arguments where given start REPL
            return WalRepl(wal).cmdloop()

        filename = args.program_path

        if filename[-3:] == '.wo':
            sexprs = wal_decode(filename)
        else:
            with open(filename, 'r', encoding='utf8') as file:
                try:
                    sexprs = read_wal_sexprs(file.read(), filename)
                except ParseError as e:
                    e.show()
                    sys.exit(os.EX_DATAERR)

        try:
            for sexpr in sexprs:
                try:
                    expanded = expand(wal.eval_context, sexpr, parent=wal.eval_context.global_environment)
                    optimized = optimize(expanded)
                    resolved = resolve(optimized, start=wal.eval_context.global_environment.environment)
                except AssertionError as error:
                    wal.print_error(sexpr, error)

                wal.eval(resolved)
        except WalEvalError as error:
            error.print()
            if args.repl_on_failure:
                WalRepl(wal, intro=WalRepl.dyn_intro).cmdloop()

            return os.EX_SOFTWARE

    return os.EX_OK
