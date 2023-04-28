'''The WAL core module'''
# pylint: disable=C0103

from wal.trace.container import TraceContainer
from wal.eval import SEval
from wal.reader import read_wal_sexpr, ParseError
from wal.ast_defs import Operator as Op
from wal.ast_defs import Symbol as S
from wal.passes import expand, optimize
from wal.install import compile_stdlib

class Wal:
    '''Main Wal class to be imported into other applications'''

    def __init__(self):  # pylint: disable=C0103
        self.traces = TraceContainer()
        self.eval_context = SEval(self.traces)
        self.eval_context.wal = self
        self.eval_context.eval([Op.REQUIRE, S('std/std')])
        compile_stdlib(self)

    def load(self, file, tid='DEFAULT', from_string=False):  # pylint: disable=C0103
        '''Load trace from file and add it using id to WAL'''
        self.traces.load(file, tid, from_string=from_string)

    def step(self, steps=1, tid=None):
        '''Step one or all traces.
        If steps is not defined step trace(s) by +1.
        If no trace id (tid) is defined step all traces.
        '''
        return self.traces.step(steps, tid)

    def eval_str(self, txt, **args):
        '''Parses and evaluates the txt argument'''
        assert isinstance(txt, str)
        try:
            sexpr = read_wal_sexpr(txt)
            return self.eval(sexpr, **args)
        except ParseError as e:
            e.show()
            return None

    def eval(self, sexpr, **args):
        '''Evaluate the WAL expression sexpr'''
        # put passed arguments into context
        for name, val in args.items():
            if self.eval_context.global_environment.is_defined(name):
                self.eval_context.global_environment.write(name, val)
            else:
                self.eval_context.global_environment.define(name, val)

        if sexpr:
            expanded = expand(self.eval_context, sexpr, parent=self.eval_context.global_environment)
            optimized = optimize(expanded)
            return self.eval_context.eval(optimized)

        # remove passed arguments from context
        for name, val in args.items():
            self.eval_context.global_environment.undefine(name)

        return None

    def run(self, sexpr, **args):
        '''Evaluate the WAL expressions sexprs from Index 0'''
        if isinstance(sexpr, str):
            sexpr = read_wal_sexpr(sexpr)

        res = None
        if sexpr:
            self.eval_context.reset()
            self.eval_context.eval([Op.REQUIRE, S('std/std')])

            for name, val in args.items():
                self.eval_context.global_environment.define(name, val)

            expanded = expand(self.eval_context, sexpr, parent=self.eval_context.global_environment)
            optimized = optimize(expanded)
            res = self.eval_context.eval(optimized)

        return res

    def run_file(self, filename):
        '''Executes a WAL program from a file'''
        with open(filename, 'r', encoding='utf-8') as fin:
            self.eval_context.eval(fin.read())
