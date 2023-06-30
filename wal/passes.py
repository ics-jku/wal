'''WAL Interpreter Passes '''
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


def resolve(expr, start={}):
    '''Variable environment resolution pass '''
    scopes=[None, dict(start)]
    def resolve_vars(expr):
        if isinstance(expr, list):
            op = expr[0]
            if op == Operator.DEFINE:
                id = expr[1]
                assert id.name not in scopes[-1], f'symbol {id} already defined'
                body = resolve_vars(expr[2])
                scopes[-1][expr[1].name] = True
                return [Operator.DEFINE, id, body]
            elif op == Operator.LET:
                env = {}
                scopes.append(env)
                for binding in expr[1]:
                    env[binding[0].name] = True

                body = [resolve_vars(sub) for sub in expr[2:]]
                scopes.pop()
                return [Operator.LET, expr[1], *body]
            elif op == Operator.LAMBDA:
                args = expr[1]
                env = {}
                scopes.append(env)
                if isinstance(args, list):
                    for arg in expr[1]:
                        assert isinstance(arg, Symbol), 'lambda: parameters must be symbols'
                        env[arg.name] = True
                elif isinstance(args, Symbol):
                    env[args.name] = True
                else:
                    assert False, 'lambda: first argument must be a list or a symbol'

                body = [resolve_vars(sub) for sub in expr[2:]]
                scopes.pop()
                return [Operator.LAMBDA, expr[1], *body]
            elif op == Operator.DEFMACRO:
                scopes[-1][expr[1].name] = True
                return expr
            elif op in [Operator.QUOTE, Operator.QUASIQUOTE, Operator.ALIAS]:
                return expr
            # elif isinstance(op, (Operatorop, S.name in operators:
            #     return [expr[0], *[resolve_vars(sub) for sub in expr[1:]]]
            else:
                return [resolve_vars(sub) for sub in expr]
        elif isinstance(expr, Symbol):
            id = expr.name
            steps = 0
            while scopes[-steps-1] is not None and id not in scopes[-steps-1]:
                steps += 1

            if scopes[-steps-1]:
                return Symbol(expr.name, steps)
            else:
                # if the symbol is not defined it still can be a signal
                # in this case just use regular slow resolution
                return expr

        # all other expression can just be returned as they are
        return expr

    return(resolve_vars(expr))



            
