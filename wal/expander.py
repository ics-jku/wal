from wal.ast_defs import Operator, Symbol, Macro, Environment


def expand(seval, exprs, parent=None):
    if isinstance(exprs, list):
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
                exprs.clear()
                for expr in expanded:
                    exprs.append(expr)
                seval.environment = save_env


        return list(map(lambda expr: expand(seval, expr), exprs))
        
    
    return exprs
