'''WAL Interpreter Passes '''
# pylint: disable=C0103,R0912,W0150
from math import prod

from wal.ast_defs import Operator, Symbol, Macro, Environment
from wal.util import wal_str


def expand(seval, exprs, parent=None):
    '''Macroexpansion Pass'''
    if isinstance(exprs, list):
        if len(exprs) > 0 and exprs[0] in [Operator.QUOTE, Operator.QUASIQUOTE]:
            return exprs
        if len(exprs) > 0 and isinstance(exprs[0], Symbol) and seval.environment.is_defined(exprs[0].name):
            expr = seval.environment.read(exprs[0].name)
            if isinstance(expr, Macro):
                macro_env = Environment(parent=parent)
                vals = exprs[1:]

                if isinstance(expr.args, Symbol):
                    macro_env.define(expr.args.name, vals)
                elif isinstance(expr.args, list):
                    assert len(expr.args) == len(vals), f'{expr.name}: number of passed arguments does not match expected number'
                    for arg, val in zip(expr.args, vals):
                        macro_env.define(arg.name, val)
                else:
                    assert False, f'cannot evaluate {wal_str(expr)}'


                save_env = seval.environment
                seval.environment = macro_env
                expanded = seval.eval(expr.expression)
                seval.environment = save_env

                if isinstance(expanded, list):
                    exprs.clear()
                    for expr in expanded:
                        exprs.append(expr)
                else:
                    return expanded


        return list(map(lambda expr: expand(seval, expr, parent=parent), exprs))


    return exprs


def optimize(expr):
    '''Optimization Pass'''
    try:
        if isinstance(expr, list):
            op = expr[0]
            if op in [Operator.QUOTE, Operator.QUASIQUOTE]:
                pass
            elif op == Operator.IF:
                expr = list(map(optimize, expr))
                if (expr[1] is True) or isinstance(expr[1], (int, float, str)):
                    if expr[1]:
                        # (if #t then else) => then
                        expr = expr[2]
                    else:
                        # (if #f/0 then else) => else
                        expr = expr[3]
            # (do expr) => expr
            elif op == Operator.DO:
                expr = list(map(optimize, expr))
                if len(expr) == 2:
                    expr = expr[1]

            elif op == Operator.ADD:
                expr = list(map(optimize, expr))
                if all(isinstance(arg, (int, float)) for arg in expr[1:]):
                    expr = sum(expr[1:])
                elif all(isinstance(arg, str) for arg in expr[1:]):
                    expr = ''.join(expr[1:])

            elif op == Operator.MUL:
                expr = list(map(optimize, expr))
                if all(isinstance(arg, (int, float)) for arg in expr[1:]):
                    expr = prod(expr[1:])

    finally:
        return expr
