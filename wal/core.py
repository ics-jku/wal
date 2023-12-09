'''The WAL core module'''

from wal.trace.container import TraceContainer
from wal.eval import SEval
from wal.reader import read_wal_sexpr, read_wal_sexprs, ParseError
from wal.ast_defs import Operator as Op
from wal.ast_defs import Symbol as S
from wal.ast_defs import UserOperator
from wal.ast_defs import WList
from wal.ast_defs import WalEvalError
from wal.passes import expand, optimize, resolve


class Wal:
    '''Main Wal class to be imported into other applications'''

    def __init__(self):  # pylint: disable=C0103
        self.traces = TraceContainer()
        self.eval_context = SEval(self.traces)
        self.eval_context.wal = self
        self.eval_context.eval(WList([Op.EVAL_FILE, S('std/std')]))
        self.eval_context.eval(WList([Op.EVAL_FILE, S('std/module')]))

    def load(self, file, tid='DEFAULT', from_string=False, keep_signals=None):
        '''Load trace from file and add it using id to WAL'''
        self.traces.load(file, tid, from_string=from_string, keep_signals=keep_signals)

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
        '''Evaluate the WAL expression sexpr and run passes'''
        # put passed arguments into context
        for name, val in args.items():
            if self.eval_context.global_environment.is_defined(name):
                self.eval_context.global_environment.write(name, val)
            else:
                self.eval_context.global_environment.define(name, val)

        res = None
        if sexpr:
            try:
                expanded = expand(self.eval_context, sexpr, parent=self.eval_context.global_environment)
                optimized = optimize(expanded)
                resolved = resolve(optimized, start=self.eval_context.global_environment.environment)
                res = self.eval_context.eval(resolved)
            except AssertionError as error:
                self.eval_context.print_error(sexpr, error)
                raise WalEvalError()

        # remove passed arguments from context
        for name, val in args.items():
            self.eval_context.global_environment.undefine(name)

        return res

    def run_str(self, txt, **args):
        '''Parses and runs the txt argument'''
        assert isinstance(txt, str)
        try:
            sexpr = read_wal_sexpr(txt)
            return self.run(sexpr, **args)
        except ParseError as e:
            e.show()
            return None

    def run(self, sexpr, **args):
        '''Evaluate the WAL expressions sexprs from Index 0'''
        res = None
        if sexpr:
            self.eval_context.reset()
            self.eval_context.eval(WList([Op.EVAL_FILE, S('std/std')]))
            self.eval_context.eval(WList([Op.EVAL_FILE, S('std/module')]))

            for name, val in args.items():
                self.eval_context.global_environment.define(name, val)

            expanded = expand(self.eval_context, sexpr, parent=self.eval_context.global_environment)
            optimized = optimize(expanded)
            resolved = resolve(optimized, start=self.eval_context.global_environment.environment)
            res = self.eval_context.eval(resolved)

        return res

    def run_file(self, filename):
        '''Executes a WAL program from a file'''
        with open(filename, 'r', encoding='utf-8') as fin:
            return self.eval(WList([Op.DO, *read_wal_sexprs(fin.read())]))


    def register_operator(self, name, function):
        self.eval_context.global_environment.define(name, UserOperator(name))
        self.eval_context.user_dispatch[name] = function


    def append_walpath(self, path):
        if path not in self.eval_context.walpath:
            self.eval_context.walpath.append(path)
            return True

        return False
