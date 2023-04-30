'''WAL Reader'''

import ast
from lark import Lark, Transformer
from lark import UnexpectedToken, UnexpectedEOF, UnexpectedCharacters
from lark.exceptions import VisitError
from wal.ast_defs import Symbol, S, Operator, Unquote, UnquoteSplice, operators


WAL_GRAMMAR = r"""
    _NL: /(\r?\n)+/
    _COMMENT: _WS? ";" /.*/
    _WS: WS
    _BASH_LINE : /\s*#![^\n]+\n/

    sexpr_strict: (atom | list | quoted | quasiquoted | unquote | unquote_splice)
    timed_sexpr : sexpr_strict "@" sexpr_strict
    _INTER : _COMMENT | _WS
    sexpr : _INTER* (sexpr_strict | timed_sexpr) _INTER*
    quoted : "'" sexpr
    quasiquoted : "`" sexpr
    unquote : "," sexpr
    unquote_splice : ",@" sexpr
    sexpr_list : _BASH_LINE? (_INTER* | sexpr*)

    atom : string
         | operator
         | symbol
         | float
         | int

    int : dec_int | bin_int | hex_int
    float : /[+-]?[0-9]+\.[0-9]*/
    dec_int : /[+-]?[0-9]+/
    bin_int : /0b[0-1]+/
    hex_int : /0x[0-9a-fA-F]+/

    bool : true | false
    true : "#t"
    false : "#f"
    symbol : base_symbol | scoped_symbol | grouped_symbol | bit_symbol | sliced_symbol
    !operator: "+" | "-" | "*" | "/" | "&&" | "||" | "=" | "!=" | ">" | "<" | ">=" | "<=" | "!" | "**"

    scoped_symbol : "~" base_symbol
    grouped_symbol : "#" base_symbol
    !base_symbol : /[a-zA-Z_\.][=$\*\/>:\.\-_\?=%§!\\~+<>|,\w]*/
    bit_symbol : sexpr_strict "[" sexpr "]"
    sliced_symbol : sexpr_strict "[" sexpr ":" sexpr "]"

    string : ESCAPED_STRING

    list : "(" [sexpr*] ")"
           | "[" [sexpr*] "]"
           | "{" [sexpr*] "}"

    %import common.ESCAPED_STRING
    %import common.WS
    """


class TreeToWal(Transformer):
    '''Transformer to create valid WAL expressions form parsed data'''
    string = lambda self, s: ast.literal_eval(s[0])

    def symbol(self, sym):
        '''Converts symbols to operators if sym is a valid operator '''
        sym = sym[0]
        if isinstance(sym, Symbol):
            return Operator(sym.name) if sym.name in operators else sym
        return sym

    quoted = lambda self, q: [Operator.QUOTE, q[0]]
    quasiquoted = lambda self, q: [Operator.QUASIQUOTE, q[0]]
    unquote = lambda self, q: Unquote(q[0])
    unquote_splice = lambda self, q: UnquoteSplice(q[0])

    operator = lambda self, o: Operator(o[0].value)
    simple_symbol = lambda self, s: s[0]
    base_symbol = lambda self, s: S(''.join(list(map(lambda x: x.value, s))))
    scoped_symbol = lambda self, s: [Operator.RESOLVE_SCOPE, s[0]]

    def grouped_symbol(self, s):
        if s[0].name == 't':
            return True
        if s[0].name == 'f':
            return False

        return [Operator.RESOLVE_GROUP, s[0]]

    

    bit_symbol = lambda self, s: [Operator.SLICE, s[0], s[1]]
    sliced_symbol = lambda self, s: [Operator.SLICE, s[0], s[1], s[2]]

    int = lambda self, i: i[0]
    float = lambda self, f: float(f[0])
    bin_int = lambda self, i: int(i[0], 2)
    dec_int = lambda self, i: int(i[0])
    hex_int = lambda self, i: int(i[0], 16)

    atom = lambda self, a: a[0]
    list = list
    bool = lambda self, b: b[0]
    true = lambda self, _: True
    false = lambda self, _: False
    sexpr = lambda self, s: s[0] if s else None
    timed_sexpr = lambda self, s: [Operator.REL_EVAL, s[0], s[1]]
    sexpr_list = list
    sexpr_strict = lambda self, s: s[0] if s else None


def read(code, reader):
    try:
        parsed = reader.parse(code.strip())
        return TreeToWal().transform(parsed)
    except UnexpectedEOF as u:
        context = u.get_context(code)
        msg = f'Unexpected end of file at  at line {u.line}:{u.column}.\nDid you forget a closing )?'
        raise ParseError(context, msg) from u
    except UnexpectedToken as u:
        context = u.get_context(code)
        msg = f'Unexpected "{u.token}" at line {u.line}:{u.column}'
        print(u)
        raise ParseError(context, msg) from u
    except UnexpectedCharacters as u:
        context = u.get_context(code)
        msg = f'Unexpected "{u.char}" at line {u.line}:{u.column}'
        print(u)
        raise ParseError(context, msg) from u
    except VisitError as u:
        context = u.__context__
        raise ParseError("", str(context)) from u


reader_sexpr = Lark(WAL_GRAMMAR, start='sexpr', parser='lalr')
def read_wal_sexpr(code):
    return read(code, reader_sexpr)


reader_sexprs = Lark(WAL_GRAMMAR, start='sexpr_list', parser='lalr')
def read_wal_sexprs(code):
    return read(code, reader_sexprs)


class ParseError(Exception):
    '''Exception thrown when a syntax error is detected'''

    def __init__(self, context, message):
        super().__init__(context + '\n' + message)

        self.context = context
        self.message = message

    def show(self):
        print(self.context)
        print(self.message)
