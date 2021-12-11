'''Main wal command line tool entry point'''
# pylint: disable=C0103

import os
import sys

from wal.core import Wal
from wal.repl import WalRepl
from wal.reader import read_wal_sexprs, ParseError


def run():
    '''Entry point for the application script'''
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()


def main():  # pylint: disable=R1710
    '''WAL main function'''
    sys.setrecursionlimit(10000)

    if len(sys.argv) == 1:
        return WalRepl().cmdloop()

    if len(sys.argv) >= 2:
        filename = sys.argv[1]

        wal = Wal()

        wal.eval_context.context['args'] = sys.argv

        if filename[-3:] == '.wo':
            sexprs = wal.decode(filename)
        else:
            with open(filename, 'r', encoding='utf8') as file:
                try:
                    sexprs = read_wal_sexprs(file.read())
                except ParseError as e:
                    e.show()
                    sys.exit(os.EX_DATAERR)

        try:
            for sexpr in sexprs:
                wal.eval(sexpr)
        except Exception as e: # pylint: disable=W0703
            print()
            print('>>>>> Runtime error! <<<<<')
            print(e)
            return os.EX_SOFTWARE

        return os.EX_OK
