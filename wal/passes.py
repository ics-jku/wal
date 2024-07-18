'''WAL Interpreter Passes '''
from math import prod

from wal.ast_defs import Operator, Symbol, Macro, Environment, WList
from wal.util import wal_str


def recursive_set_line_info(expr, line_info):
  if isinstance(expr, (WList, list)):
    return WList([recursive_set_line_info(sub, line_info) for sub in expr], line_info=line_info)
  elif isinstance(expr, Symbol):
    expr.line_info = line_info
    return expr
  else:
    return expr


def expand(seval, exprs, parent=None):
    '''Macroexpansion Pass'''
    if isinstance(exprs, (WList, list)):
        if len(exprs) > 0 and exprs[0] in [Operator.QUOTE, Operator.QUASIQUOTE]:
            return exprs
        if len(exprs) > 0 and isinstance(exprs[0], Symbol) and seval.environment.is_defined(exprs[0].name):
            expr = seval.environment.read(exprs[0].name)
            if isinstance(expr, Macro):
                macro_env = Environment(parent=parent)
                vals = exprs[1:]

                if isinstance(expr.args, Symbol):
                    macro_env.define(expr.args.name, vals)
                elif isinstance(expr.args, WList):
                    assert len(expr.args) == len(vals), f'{expr.name}: number of passed arguments does not match expected number'
                    for arg, val in zip(expr.args, vals):
                        macro_env.define(arg.name, val)
                else:
                    assert False, f'cannot evaluate {wal_str(expr)}'

                save_env = seval.environment
                seval.environment = macro_env
                expanded = seval.eval(expr.expression)
                expanded.line_info = exprs[0].line_info
                expanded = expand(seval, expanded, parent)

                seval.environment = save_env

                if isinstance(expanded, WList):
                    exprs.clear()
                    for expr in expanded:
                        exprs.append(expr)
                else:
                    return expanded


        line_info = exprs.line_info if isinstance(exprs, WList) else None
        exprs = WList(list(map(lambda expr: expand(seval, expr, parent=parent), exprs)), line_info=line_info)
    
    return exprs


def optimize(expr):
    '''Optimization Pass'''
    try:
        if isinstance(expr, (WList, list)):
            op = expr[0]
            if op in [Operator.QUOTE, Operator.QUASIQUOTE]:
                pass
            elif op == Operator.IF:
                expr = WList(list(map(optimize, expr)), line_info=expr.line_info)
                if (expr[1] is True) or isinstance(expr[1], (int, float, str)):
                    if expr[1]:
                        # (if #t then else) => then
                        expr = expr[2]
                    else:
                        # (if #f/0 then else) => else
                        expr = expr[3]
            # (do expr) => expr
            elif op == Operator.DO:
                expr = WList(list(map(optimize, expr)), line_info=expr.line_info)
                if len(expr) == 2:
                    expr = optimize(expr[1])

            elif op == Operator.ADD:
                expr = WList(list(map(optimize, expr)), line_info=expr.line_info)
                if all(isinstance(arg, (int, float)) for arg in expr[1:]):
                    expr = sum(expr[1:])
                elif all(isinstance(arg, str) for arg in expr[1:]):
                    expr = ''.join(expr[1:])

            elif op == Operator.MUL:
                expr = WList(list(map(optimize, expr)), line_info=expr.line_info)
                if any(arg == 0 for arg in expr[1:]):
                    expr = 0
                if all(isinstance(arg, (int, float)) for arg in expr[1:]):
                    expr = prod(expr[1:])

            elif op == Operator.AND:
                # (&& x) => x
                if len(expr) == 2:
                    expr = expr[1]
                elif any(not arg for arg in expr[1:]):
                    expr = False
                elif all(isinstance(arg, (int, float, str)) and arg != 0 for arg in expr[1:]):
                    expr = True

            elif op == Operator.OR:
                # (|| x) => x
                if len(expr) == 2:
                    expr = expr[1]
                elif any(isinstance(arg, (int, float, str)) and arg != 0 for arg in expr[1:]):
                    expr = True
                elif all(not arg for arg in expr[1:]):
                    expr = False
            else:
                expr = WList(list(map(optimize, expr)), line_info=expr.line_info)

    finally:
        return expr


def resolve(expr, start={}):
    '''Variable environment resolution pass '''
    scopes=[None, dict(start)]
    def resolve_vars(expr):
        if isinstance(expr, WList) and len(expr) > 0:
            op = expr[0]
            if op == Operator.DEFINE:
                id = expr[1]
                assert id.name not in scopes[-1], f'symbol {id} already defined'
                body = resolve_vars(expr[2])
                scopes[-1][expr[1].name] = True
                return WList([Operator.DEFINE, id, body], line_info=expr.line_info)
            elif op == Operator.LET:
                env = {}
                scopes.append(env)
                for binding in expr[1]:
                    env[binding[0].name] = True

                body = [resolve_vars(sub) for sub in expr[2:]]
                scopes.pop()
                return WList([Operator.LET, expr[1], *body], line_info=expr.line_info)
            elif op == Operator.FN:
                args = expr[1]
                env = {}
                scopes.append(env)
                if isinstance(args, (WList, list)):
                    for arg in expr[1]:
                        assert isinstance(arg, Symbol), 'fn: parameters must be symbols'
                        env[arg.name] = True
                elif isinstance(args, Symbol):
                    env[args.name] = True
                else:
                    assert False, 'fn: first argument must be a list or a symbol'

                body = [resolve_vars(sub) for sub in expr[2:]]
                scopes.pop()
                return WList([Operator.FN, expr[1], *body])
            elif op == Operator.DEFMACRO:
                scopes[-1][expr[1].name] = True
                return expr
            elif op in [Operator.QUOTE, Operator.QUASIQUOTE, Operator.ALIAS]:
                return expr
            else:
                return WList([resolve_vars(sub) for sub in expr], line_info=expr.line_info)
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

        # all other expressions can just be returned as they are
        return expr

    return(resolve_vars(expr))

