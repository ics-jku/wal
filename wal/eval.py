'''S-Exprssion eval functions'''
from wal.util import wal_str
from wal.ast_defs import Operator, Symbol, ExpandGroup, Environment, Closure, Macro
from wal.implementation.types import type_operators
from wal.implementation.list import list_operators
from wal.implementation.array import array_operators
from wal.implementation.wal import wal_operators
from wal.implementation.core import core_operators
from wal.implementation.special import special_operators
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
        self.dispatch = {**core_operators, **type_operators, **list_operators, **array_operators, **wal_operators, **special_operators}

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
        self.context = {
            'CS': '',
            'CG': '',
            'args': [],
        }


    def eval_args(self, args):
        '''Helper function to evaluate each element of a list'''
        return list(map(self.eval, args))

    def eval_dispatch(self, oprtr, args):
        '''Evaluate all functions dealing with lists'''
        return self.dispatch.get(oprtr.value, lambda a, b: NotImplementedError())(self, args)

    def eval_closure(self, closure, args):
        '''Evaluate a closure.'''
        save_env = self.environment
        new_env = Environment(parent=closure.environment)
        self.environment = new_env

        if isinstance(closure.args, Symbol):
            new_env.define(closure.args.name, args)
        elif isinstance(closure.args, list):
            assert len(closure.args) == len(args), f'{closure.name}: number of passed arguments does not match expected number'
            for arg, val in zip(closure.args, args):
                new_env.define(arg.name, val)
        else:
            assert False, f'cannot evaluate {wal_str(closure)}'

        res = self.eval(closure.expression)
        self.environment = save_env
        return res

    def eval(self, expr):
        '''Main s-expression eval function'''
        res = NotImplementedError() # NotImplementedError(str(expr))

        if isinstance(expr, Symbol):
            name = expr.name
            if expr.name in self.aliases: # if an alias exists
                name = self.aliases[expr.name]

            if self.traces.contains(name):  # if symbol is a signal from wavefile
                res = self.traces.signal_value(name, scope=self.scope) # env[symbol_id]
            else:
                res = self.environment.read(name)
        elif isinstance(expr, list):
            head = expr[0]
            tail = []
            for element in expr[1:]:
                if isinstance(element, ExpandGroup):
                    tail += element.elements
                else:
                    tail.append(element)

            if isinstance(head, Operator):
                res = self.eval_dispatch(head, tail)
            elif isinstance(head, Closure):
                res = self.eval_closure(head, tail)
            elif isinstance(head, Macro):
                expanded = self.eval(head.expression)
                expr.clear()
                for expression in expanded:
                    expr.append(expression)
                res = self.eval(expr)
            elif isinstance(head, (int, str)):
                assert False, f'{wal_str(expr)} is not a valid function call'
            else:
                func = self.eval(head)
                res = self.eval([func] + tail)
        elif isinstance(expr, (int, str, Closure)):
            res = expr
        elif isinstance(expr, ExpandGroup):
            res = list(map(self.eval, expr.elements))

        if not isinstance(res, Exception):
            return res
        raise NotImplementedError(str(expr))
