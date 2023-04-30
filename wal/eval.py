'''S-Exprssion eval functions'''
from wal.util import wal_str
from wal.ast_defs import Operator, UserOperator, Symbol, Environment, Closure, Macro
from wal.implementation.types import type_operators
from wal.implementation.math import math_operators
from wal.implementation.list import list_operators
from wal.implementation.array import array_operators
from wal.implementation.wal import wal_operators
from wal.implementation.core import core_operators
from wal.implementation.special import special_operators
from wal.implementation.virtual import virtual_operators
# pylint: disable=R0912,R0915,R0914,too-many-instance-attributes


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
        elif isinstance(closure.args, list):
            assert len(closure.args) == len(args), f'{closure.name}: number of passed arguments does not match expected number'
            for arg, val in zip(closure.args, args):
                new_env.define(arg.name, self.eval(val))
        else:
            assert False, f'cannot evaluate {wal_str(closure)}'

        self.environment = new_env
        res = self.eval(closure.expression)
        self.environment = save_env
        return res

    def eval(self, expr):
        '''Main s-expression eval function'''
        res = NotImplementedError()

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
                    
            if self.traces.contains(name):  # if symbol is a signal from wavefile
                res = self.traces.signal_value(name, scope=self.scope) # env[symbol_id]
            else:
                # this symbol has not been resolved
                res = self.environment.read(name)
        elif isinstance(expr, list):
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

        if not isinstance(res, Exception):
            return res
        raise NotImplementedError(str(expr))
