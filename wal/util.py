''' Utility functions for WAL'''
from wal.ast_defs import Symbol, Operator

def wal_str(sexpr):
    '''Returns a string representation of a WAL expression'''
    if isinstance(sexpr, list):
        if len(sexpr) == 3 and sexpr[0] == Operator.REL_EVAL:
            txt = f'{sexpr[1].name}@sexpr[2]'
        else:
            txt = '(' + ' '.join(map(wal_str, sexpr)) + ')'
    elif isinstance(sexpr, Symbol):
        txt = sexpr.name
    elif isinstance(sexpr, Operator):
        txt = sexpr.value
    elif isinstance(sexpr, str):
        txt = f'"{sexpr}"'
    elif isinstance(sexpr, bool):
        txt = '#t' if sexpr else '#f'
    else:
        txt = str(sexpr)

    return txt
