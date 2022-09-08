''' Utility functions for WAL'''
from wal.ast_defs import Symbol, Operator

def wal_str(sexpr):
    '''Returns a string representation of a WAL expression'''
    if isinstance(sexpr, list):
        if len(sexpr) == 2 and sexpr[0] == Operator.QUOTE:
            txt = f"'{wal_str(sexpr[1])}"
        elif len(sexpr) == 3 and sexpr[0] == Operator.REL_EVAL:
            txt = f'{sexpr[1].name}@sexpr[2]'
        elif len(sexpr) > 0 and sexpr[0] == Operator.ARRAY:
            txt = '{' + ' '.join(map(wal_str, sexpr)) + '}'
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
    elif isinstance(sexpr, dict):
        content = []
        for key, value in sexpr.items():
            content.append('("' + key + '" ' + wal_str(value) + ')')

        txt = '{' + ' '.join(content) + '}'
    else:
        txt = str(sexpr)

    return txt
