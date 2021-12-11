'''S-Exprssion eval functions'''
from wal.ast_defs import Operator, Symbol, ExpandGroup
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
        self.reset()
        self.dispatch = {**core_operators, **list_operators, **array_operators, **wal_operators, **special_operators}

    def reset(self):
        '''Resets all traces back to time 0 and resets all WAL elements (e.g. aliases, imports, ...) '''
        # roll back traces
        for trace in self.traces.traces.values():
            trace.set(0)

        self.stack = []
        self.imports = {}
        self.aliases = {}
        self.scope = ''
        self.group = ''
        self.context = {
            'CS': '',
            'CG': ''
        }


    def eval_args(self, args):
        '''Helper function to evaluate each element of a list'''
        return list(map(self.eval, args))

    def eval_dispatch(self, oprtr, args):
        '''Evaluate all functions dealing with lists'''
        return self.dispatch.get(oprtr.value, lambda a, b: NotImplementedError())(self, args)


    def eval_lambda(self, lambda_expr, vals):
        '''Evaluate lambda expressions'''
        sub_context = {}
        bindings = []
        for i in range(len(lambda_expr[1])):
            arg = lambda_expr[1][i]
            if isinstance(arg, list):
                assert len(arg) == 2, 'lambda: only one value can be bound to a symbol (sym expr)'
                assert isinstance(arg[0], Symbol), 'lambda: first argument of binding must be a symbol'
                sub_context[arg[0].name] = self.eval(arg[1])
                bindings.append(arg[0])

        assert len(lambda_expr[1]) - len(bindings) == len(
            vals), f'lambda: number of passed arguments must match signature {lambda_expr[1]}'

        for arg, val in zip(lambda_expr[1], vals):
            if isinstance(arg, Symbol):
                sub_context[arg.name] = self.eval(val)
        self.stack.append(sub_context)
        res = self.eval(lambda_expr[2])
        self.stack.pop()

        # get value of bounded variables
        for binding in bindings:
            if self.stack:
                self.stack[-1][binding.name] = sub_context[binding.name]
            else:
                self.context[binding.name] = sub_context[binding.name]

        return res

    def eval(self, expr):
        '''Main s-expression eval function'''
        res = NotImplementedError() # NotImplementedError(str(expr))

        if isinstance(expr, list):
            head = expr[0]
            #tail = [s for s in e.elements if isinstance(e, ExpandGroup) else e for e in expr[1:]]
            tail = []
            for element in expr[1:]:
                if isinstance(element, ExpandGroup):
                    tail += element.elements
                else:
                    tail.append(element)

            if isinstance(head, Operator):
                res = self.eval_dispatch(head, tail)
            elif isinstance(head, Symbol):
                if self.stack and head.name in self.stack[-1]:
                    val = self.stack[-1][head.name]
                else:
                    val = self.context[head.name]
                if isinstance(val, list):
                    if val[0] == Operator.LAMBDA or val[0] == Operator.FN:
                        res = self.eval_lambda(val, tail)
            elif isinstance(head, list):
                if isinstance(head[0], Operator):
                    if head[0] == Operator.LAMBDA:
                        res = self.eval_lambda(head, tail)

        else:
            if isinstance(expr, Symbol):
                name = expr.name
                if expr.name in self.aliases: # if an alias exists
                    name = self.aliases[expr.name]
                if self.traces.contains(name):  # if symbol is a signal from wavefile
                    res = self.traces.signal_value(name, scope=self.scope) # env[symbol_id]
                else:
                    if self.stack and name in self.stack[-1]:  # if symbol existst in local scope
                        res = self.stack[-1][name]
                    elif name in self.context:  # if symbol is not in stack but in global scope
                        res = self.context[name]
                    else:
                        self.context[name] = 0  # implicit initialization of variabels on first use
                        res = 0
            elif isinstance(expr, int):
                res = expr
            elif isinstance(expr, str):
                res = expr
            elif isinstance(expr, ExpandGroup):
                res = list(map(self.eval, expr.elements))

        if not isinstance(res, Exception):
            return res
        raise NotImplementedError(str(expr))
