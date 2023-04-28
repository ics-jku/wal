'''wal command line compiler'''
import argparse
import pickle
from pathlib import Path
from wal.version import __version__

from wal.reader import read_wal_sexprs
from wal.passes import expand, optimize


class Arguments:  # pylint: disable=too-few-public-methods
    '''Wrapper class for argument parser'''

    def __init__(self):
        parser = argparse.ArgumentParser()
        self.parser = parser

        parser.add_argument('input_name', help='input filename')
        parser.add_argument('-o', action='store', dest='output_name',
                            help='output filename', default=None)
        parser.add_argument('-v', '--version', action='version',
                            version=f'%(prog)s {__version__}')

    def parse(self):
        '''Parse program arguments and check minimal requirements'''
        args = self.parser.parse_args()

        if args.input_name is None:
            return None
        return args


def wal_compile(inname, outname, wal):
    '''Compiles the file inname to outname'''
    with open(inname, 'r', encoding='utf8') as fin:
        code = fin.read()
        compiled = []

        for sexpr in read_wal_sexprs(code):
            expanded = expand(wal.eval_context, sexpr, parent=wal.eval_context.global_environment)
            optimized = optimize(expanded)
            compiled.append(optimized)

        if outname:
            name = outname
        else:
            name = Path(inname).with_suffix('.wo')

        with open(name, 'wb') as fout:
            pickle.dump(compiled, fout)


def run():  # pylint: disable=R1710
    '''Entry point for the compiler script'''

    arg_parser = Arguments()
    args = arg_parser.parse()

    from wal.core import Wal
    wal_compile(args.input_name, args.output_name, Wal())
