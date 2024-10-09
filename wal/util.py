''' Utility functions for WAL'''
# pylint: disable=R0912

import pickle
from wal.ast_defs import Symbol, Operator, Closure, Macro, Unquote, UnquoteSplice, WList


def wal_str(sexpr):
    '''Returns a string representation of a WAL expression'''
    if isinstance(sexpr, (list, WList)):
        if len(sexpr) == 2 and sexpr[0] == Operator.QUOTE:
            txt = f"'{wal_str(sexpr[1])}"
        elif len(sexpr) == 2 and sexpr[0] == Operator.QUASIQUOTE:
            txt = f"`{wal_str(sexpr[1])}"
        elif len(sexpr) == 2 and sexpr[0] == Operator.UNQUOTE:
            txt = f",{wal_str(sexpr[1])}"
        elif len(sexpr) == 3 and sexpr[0] == Symbol('reval'):
            txt = f'{wal_str(sexpr[1])}@{sexpr[2]}'
        elif len(sexpr) > 0 and sexpr[0] == Operator.ARRAY:
            txt = '{' + ' '.join(map(wal_str, sexpr)) + '}'
        else:
            txt = '(' + ' '.join(map(wal_str, sexpr)) + ')'
    elif isinstance(sexpr, Symbol):
        txt = sexpr.name
    elif isinstance(sexpr, Macro):
        txt = f'Macro: {sexpr.name}\nArgs: {wal_str(sexpr.args)}\n' + wal_str(sexpr.expression)
    elif isinstance(sexpr, Closure):
        txt = f'Function: {sexpr.name}\nArgs: {wal_str(sexpr.args)}\n' + wal_str(sexpr.expression)
    elif isinstance(sexpr, Unquote):
        txt = f',{wal_str(sexpr.content)}'
    elif isinstance(sexpr, UnquoteSplice):
        txt = f',@{wal_str(sexpr.content)}'
    elif isinstance(sexpr, Operator):
        txt = sexpr.value
    elif isinstance(sexpr, str):
        sexpr = sexpr.replace("\"", "\\\"")
        txt = f'"{sexpr}"'
    elif isinstance(sexpr, bool):
        txt = 'true' if sexpr else 'false'
    elif isinstance(sexpr, dict):
        content = []
        for key, value in sexpr.items():
            content.append('("' + key + '" ' + wal_str(value) + ')')

        txt = '{' + ' '.join(content) + '}'
    else:
        txt = str(sexpr)

    return txt


def wal_decode(filename):
    '''Decodes a compiled WAL file and returns its WAL expressions'''
    with open(filename, 'br') as fin:
        return pickle.load(fin)


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    HEADER = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def red(txt):
        return f'{Colors.RED}{txt}{Colors.END}'

    def green(txt):
        return f'{Colors.GREEN}{txt}{Colors.END}'

    def yellow(txt):
        return f'{Colors.YELLOW}{txt}{Colors.END}'

    def blue(txt):
        return f'{Colors.BLUE}{txt}{Colors.END}'

    def purple(txt):
        return f'{Colors.PURPLE}{txt}{Colors.END}'

    def header(txt):
        return f'{Colors.HEADER}{txt}{Colors.END}'

    def bold(txt):
        return f'{Colors.BOLD}{txt}{Colors.END}'        
    
    def underline(txt):
        return f'{Colors.UNDERLINE}{txt}{Colors.END}'        
