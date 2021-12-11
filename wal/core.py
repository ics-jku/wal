'''The WAL core module'''
# pylint: disable=C0103

import pickle

from wal.trace import TraceContainer
from wal.eval import SEval
from wal.reader import read_wal_sexpr, ParseError
from wal.ast_defs import Symbol, Operator

class Wal:
    '''Main Wal class to be imported into other applications'''

    def __init__(self):  # pylint: disable=C0103
        self.traces = TraceContainer()
        self.eval_context = SEval(self.traces)

    def load(self, file, tid='DEFAULT', from_string=False):  # pylint: disable=C0103
        '''Load trace from file and add it using id to WAL'''
        self.traces.load(file, tid, from_string=from_string)

    def step(self, steps=1, tid=None):
        '''Step one or all traces.
        If steps is not defined step trace(s) by +1.
        If no trace id (tid) is defined step all traces.
        '''
        return self.traces.step(steps, tid)

    def eval(self, sexpr, **args):
        '''Evaluate the WAL expression sexpr'''
        if isinstance(sexpr, str):
            try:
                sexpr = read_wal_sexpr(sexpr)
            except ParseError as e:
                e.show()
                return None

        # put passed arguments into context
        for name, val in args.items():
            self.eval_context.context[name] = val

        if sexpr:
            return self.eval_context.eval(sexpr)

        # remove passed arguments from context
        for name, val in args.items():
            del self.eval_context.context[name]

        return None

    def run(self, sexpr, **args):
        '''Evaluate the WAL expression sexpr from Index 0'''
        if isinstance(sexpr, str):
            sexpr = [read_wal_sexpr(sexpr)]

        res = None
        if sexpr:
            self.eval_context.reset()

            for name, val in args.items():
                self.eval_context.context[name] = val

            for expr in sexpr:
                res = self.eval_context.eval(expr)

        return res

    # pylint: disable=R0201
    def decode(self, filename):
        '''Decodes a compiled WAL file and returns its WAL expressions'''
        with open(filename, 'br') as fin:
            return pickle.load(fin)



def wal_str(sexpr):
    '''Returns a string representation of a WAL expression'''
    if isinstance(sexpr, list):
        if len(sexpr) == 3 and sexpr[0] == Operator.REL_EVAL:
            txt = f'{sexpr[1].name}@sexpr[2]'
        else:
            txt = '(' + ' '.join(map(wal_str, sexpr)) + ')'
    elif isinstance(sexpr, Symbol):
        txt = sexpr.name
    elif isinstance(sexpr, Operator):
        txt = sexpr.value
    elif isinstance(sexpr, str):
        txt = f'"{sexpr}"'
    elif isinstance(sexpr, bool):
        txt = '#t' if sexpr else '#f'
    else:
        txt = str(sexpr)

    return txt
