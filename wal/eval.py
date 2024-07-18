'''S-Exprssion eval functions'''

import os
import wal

from importlib.resources import files

from wal.util import wal_str
from wal.ast_defs import Operator, UserOperator, Symbol, Environment, Closure, Macro, WList, WalEvalError
from wal.implementation.types import type_operators
from wal.implementation.math import math_operators
from wal.implementation.list import list_operators
from wal.implementation.array import array_operators
from wal.implementation.wal import wal_operators
from wal.implementation.core import core_operators
from wal.implementation.special import special_operators
from wal.implementation.virtual import virtual_operators


class SEval:
    '''Evaluate s-expressions'''

    def __init__(self, traces):
        '''Initial Evaluation Object'''
        self.traces = traces
        self.global_environment = None
        self.environment = None
        self.gensymi = None
        self.imports = None
        self.aliases = None
        self.macros = None
        self.scope = None
        self.group = None
        self.context = None
        self.reset()
        self.dispatch = {**core_operators, **math_operators, **type_operators, \
            **list_operators, **array_operators, **wal_operators, \
            **special_operators, **virtual_operators}
        self.user_dispatch = {}
        initial_walpath = ['.', os.path.expanduser('~/.wal/libs/'), str(files(wal).joinpath('libs/'))]
        self.walpath = initial_walpath + os.getenv('WALPATH', '').split(';')

    def reset(self):
        '''Resets all traces back to time 0 and resets all WAL elements (e.g. aliases, imports, ...) '''
        # roll back traces
        for trace in self.traces.traces.values():
            trace.set(0)

        self.global_environment = Environment()
        self.environment = self.global_environment
        self.gensymi = 0
        self.imports = {}
        self.aliases = {}
        self.macros = {}
        self.scope = ''
        self.group = ''
        self.virtual_signals = {}
        self.global_environment.define('CS', '')
        self.global_environment.define('CG', '')
        self.global_environment.define('args', [])
        self.global_environment.define('VIRTUAL', self.virtual_signals)

    def eval_args(self, args):
        '''Helper function to evaluate each element of a list'''
        return list(map(self.eval, args))

    def eval_dispatch(self, oprtr, args):
        '''Dispatch operators'''
        return self.dispatch.get(oprtr.value, lambda a, b: NotImplementedError())(self, args)

    def eval_user_dispatch(self, oprtr, args):
        '''Dispatch operators added by the user'''
        return self.user_dispatch.get(oprtr.name, lambda a, b: NotImplementedError())(self, args)

    def eval_closure(self, closure, args):
        '''Evaluate a closure.'''
        save_env = self.environment
        new_env = Environment(parent=closure.environment)

        if isinstance(closure.args, Symbol):
            new_env.define(closure.args.name, self.eval_args(args))
        elif isinstance(closure.args, WList):
            assert len(closure.args) == len(args), f'{closure.name}: number of passed arguments does not match expected number'
            for arg, val in zip(closure.args, args):
                new_env.define(arg.name, self.eval(val))
        else:
            assert False, f'cannot evaluate {wal_str(closure)}'

        self.environment = new_env
        try:
            res = self.eval(closure.expression)
        except WalEvalError as error:
            error.add(closure.name)
            raise error

        self.environment = save_env
        return res

    def eval(self, expr):
        '''Main s-expression eval function'''
        res = NotImplementedError()
        try:
            if isinstance(expr, Symbol):
                name = expr.name
                if expr.name in self.aliases: # if an alias exists
                    name = self.aliases[expr.name]

                # this symbol was already resolved
                if expr.steps is not None:
                    env = self.environment
                    steps = expr.steps
                    while steps > 0:
                        env = self.environment.parent
                        steps -= 1

                    res = env.read(expr.name)
                elif self.traces.contains(name):  # if symbol is a signal from wavefile
                    res = self.traces.signal_value(name, scope=self.scope)
                else:
                    # this symbol has not been resolved
                    res = self.environment.read(name)
            elif isinstance(expr, (WList, list)):
                head = expr[0]
                tail = expr[1:]

                if isinstance(head, Operator):
                    res = self.eval_dispatch(head, tail)
                elif isinstance(head, Closure):
                    res = self.eval_closure(head, tail)
                elif isinstance(head, UserOperator):
                    res = self.eval_user_dispatch(head, tail)
                elif isinstance(head, Macro):
                    expanded = self.eval(head.expression)
                    expr.clear()
                    for expression in expanded:
                        expr.append(expression)
                    res = self.eval(expr)
                elif callable(expr[0]):
                    res = expr[0](*expr[1:])
                elif isinstance(head, (int, str)):
                    assert False, f'{wal_str(expr)} is not a valid function call'
                else:
                    func = self.eval(head)
                    res = self.eval([func] + tail)
            elif isinstance(expr, (int, str, float, Closure)):
                res = expr
        except AssertionError as error:
            self.print_error(expr, error)
            raise WalEvalError()

        if not isinstance(res, Exception):
            return res
        raise NotImplementedError(str(expr))


    def print_error(self, expr, error):
        print()
        print('>>>>> WAL Runtime error! <<<<<')
        if isinstance(expr, (WList, Symbol)) and expr.line_info and expr.line_info['filename'] != '':
            with open(expr.line_info['filename']) as f:
                lines = f.readlines()
                error_range = range(expr.line_info['line'] - 5, expr.line_info['end_line'])
                max_line_nr_width = max([len(str(lnr)) for lnr in error_range])

                for lnr in error_range:
                    if lnr >= 0:
                        line = lines[lnr].rstrip()
                        if lnr+1 >= expr.line_info['line'] and lnr+1 <= expr.line_info['end_line']:
                            print(f'\033[91m{lnr+1:{max_line_nr_width}}:\033[0m ', end='')
                        else:
                            print(f'{lnr+1:{max_line_nr_width}}: ', end='')

                        for cnr, char in enumerate(line):
                            if lnr + 1 == expr.line_info['line'] and (cnr + 1) == expr.line_info['column']:
                                print('\033[91m', end='')

                            print(char, end='')
                            if lnr + 1 == expr.line_info['end_line'] and cnr + 2 == expr.line_info['end_column']:
                                print('\033[0m', end='')

                        print()

                print(' ' * (max_line_nr_width + 1), end='')
                for cnr, char in enumerate(lines[expr.line_info['line'] - 1]):
                    if char.isspace():
                        print(char, end='')
                    elif cnr == expr.line_info['column']:
                        print('\033[91m^\033[0m', end='')
                    else:
                        print(' ', end='')

            print()
            if expr.line_info['filename']:
                print('Error at ', expr.line_info['filename'], ':', expr.line_info['line'], sep='')
            else:
                print('Error on line', expr.line_info['line'])

            print('\033[0m', end='')

        print(error)
