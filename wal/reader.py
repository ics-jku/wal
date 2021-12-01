'''WAL Reader'''
import ast
import sys
from lark import Lark, Transformer
from lark import UnexpectedInput, UnexpectedToken, UnexpectedEOF, UnexpectedCharacters
from wal.ast_defs import Symbol, ExpandGroup, S, Operator
from wal.trace import Trace

operators = [op.value for op in Operator]

wal_grammar = r"""
    _NL: /(\r?\n)+\s*/

    sexpr_strict: (atom | list | quoted)
    ?sexpr : _WS? sexpr_strict _WS?
    quoted : "'" sexpr

    line : sexpr | _COMMENT | _WS
    _BASH_LINE : /\s*#![^\n]+\n/
    sexpr_list : _BASH_LINE? line*
 
    atom : string
         | int
         | bool
         | symbol

    int : dec_int | bin_int | hex_int
    dec_int : INT | SIGNED_INT
    bin_int : /0b[0-1]+/
    hex_int : /0x[0-9a-fA-F]+/
       
    bool : true | false
    true : "#t"
    false : "#f"
    symbol : simple_symbol | sliced_symbol | bit_symbol | operator
    !operator: "+" | "-" | "*" | "/" | "&&" | "||" | "=" | "!=" | ">" | "<" | ">=" | "<=" | "!" | "**"
    simple_symbol : base_symbol | scoped_symbol | grouped_symbol | timed_symbol | bit_symbol | sliced_symbol | timed_list
    scoped_symbol : "~" base_symbol
    grouped_symbol : "#" base_symbol
    timed_symbol : sexpr_strict "@" SIGNED_INT
    timed_list : sexpr_strict "@" "(" [INT (_WS INT)*] ")"
    !base_symbol : (LETTER | "_")(LETTER | /[0-9]/ | "_" | "-" | "$" | "." | "/")*
    bit_symbol : simple_symbol "[" INT "]"
    sliced_symbol : simple_symbol "[" INT ":" INT "]"
 
    string : ESCAPED_STRING

    list : "(" [sexpr (_WS sexpr)*] ")"
           | "[" [sexpr (_WS sexpr)*] "]"
           | "{" [sexpr (_WS sexpr)*] "}"

    _COMMENT: _WS? /;[^\n]*\n/
    _WS: WS

    %import common.ESCAPED_STRING
    %import common.SIGNED_INT
    %import common.INT
    %import common.WORD
    %import common.WS
    %import common.LETTER
    """

class TreeToWal(Transformer):
    string = lambda self, s: ast.literal_eval(s[0])

    def symbol(self, s):
        s = s[0]
        if isinstance(s, Symbol):
            return Operator(s.name) if s.name in operators else s
        return s

    quoted = lambda self, q: [Operator.QUOTE, q[0]]
    
    operator = lambda self, o: S(o[0].value)
    simple_symbol = lambda self, s: s[0]
    base_symbol = lambda self, s: S(''.join(list(map(lambda x: x.value, s))))    
    scoped_symbol = lambda self, s: [Operator.SCOPED, s[0]]
    grouped_symbol = lambda self, s: [Operator.RESOLVE_GROUP, s[0]]
    timed_symbol = lambda self, s: [Operator.REL_EVAL, s[0], s[1]]
    timed_list = lambda self, s: ExpandGroup([[Operator.REL_EVAL, s[0], time] for time in s[1]])
    bit_symbol = lambda self, s: [Operator.SLICE, s[0], s[1]]
    sliced_symbol = lambda self, s: [Operator.SLICE, s[0], s[1], s[2]]

    int = lambda self, i: i[0]
    bin_int = lambda self, i: int(i[0], 2)
    dec_int = lambda self, i: int(i[0])
    hex_int = lambda self, i: int(i[0], 16)
    #INT = dec_int
    SIGNED_INT = lambda self, i: int(i.value)
    
    atom = lambda self, a: a[0]
    list = list
    bool = lambda self, b: b[0]
    true = lambda self, _: True
    false = lambda self, _: False
    sexpr_list = list
    sexpr_strict = lambda self, s: s[0]
    line = lambda self, l: l[0] if l else None


def read(code, start='sexpr'):
    try:
        reader = Lark(wal_grammar, start=start)
        parsed = reader.parse(code)
        return TreeToWal().transform(parsed)
    except UnexpectedEOF as u:
        context = u.get_context(code)
        msg = f'Unexpected end of file at  at line {u.line}:{u.column}.\nDid you forget a closing )?'
        raise ParseError(context, msg)
    except UnexpectedToken as u:
        context = u.get_context(code)
        msg = f'Unexpected "{u.token}" at line {u.line}:{u.column}'
        raise ParseError(context, msg)
    except UnexpectedCharacters as u:
        context = u.get_context(code)
        msg = f'Unexpected "{u.char}" at line {u.line}:{u.column}'
        raise ParseError(context, msg)


def read_wal_sexpr(code):
    return read(code, 'sexpr')

        
def read_wal_sexprs(code):
    return read(code, 'sexpr_list')


class ParseError(Exception):

    def __init__(self, context, message):
        super().__init__(context + '\n' + message)
        
        self.context = context
        self.message = message

    def show(self):
        print(self.context)
        print(self.message)
