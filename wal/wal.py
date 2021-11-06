'''Main wal command line tool entry point'''
import os
import sys

from wal.core import Wal
from wal.parsers import sexpr
from wal.repl import WalRepl

def run():  # pylint: disable=R1710
    '''Entry point for the application script'''
    sys.setrecursionlimit(5000)

    if len(sys.argv) == 1:
        return WalRepl().cmdloop()

    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r', encoding='utf8') as file:
            sexprs = sexpr.many().parse(file.read())
            wal = Wal()
            for form in sexprs:
                wal.eval(form)

        return os.EX_OK
