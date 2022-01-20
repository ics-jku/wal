'''Parsers for WAWK'''
# pylint: disable=C0103,R0201,C0116
from lark import Lark, Transformer
from wawk.ast_defs import Statement
from wal.ast_defs import S
from wal.ast_defs import Operator as Op

WAWK_GRAMMAR = r"""
    ?expr: symbol
         | fcall
         | forstmt
         | assign
         | block
         | array_op
         | cond
         | in_scope
         | in_group
         | "(" expr ")"
         | string
         | list
         | arith
         | SIGNED_INT -> number
         | INT -> number

    list : "[" [expr ("," expr)*] "]"

    forstmt: forin | forinarray | forvar
    forin: "for" "(" base_symbol "in" (list | fcall | base_symbol) ")" block
    forinarray: "for" "(" base_symbol "," base_symbol "in" (fcall | base_symbol) ")" block
    forvar: "for" "(" assign_std ";" expr ";" expr  ")" block

    cond : ifstmt
    ifstmt : "if" "(" expr ")" expr ("else" expr)?

    symbol : simple_symbol | sliced_symbol | bit_symbol
    simple_symbol : base_symbol | scoped_symbol | grouped_symbol | timed_symbol | bit_symbol | sliced_symbol
    scoped_symbol : "~" base_symbol
    grouped_symbol : "#" base_symbol
    timed_symbol : base_symbol "@" SIGNED_INT
    !base_symbol : (LETTER | "_") (LETTER | INT | "_" | "$" | ".")*
    bit_symbol : simple_symbol "[" INT "]"
    sliced_symbol : simple_symbol "[" INT ":" INT "]"

    arith : expr b_op expr | u_op expr
    !b_op : "+" | "-" | "*" | "/" | "&&" | "||" | "==" | "!=" | ">" | "<" | ">=" | "<="
    !u_op : "!"

    block : "{" (expr ";")* "}"
    assign : assign_arith | assign_std
    assign_std : base_symbol "=" expr
    !assign_arith : base_symbol ("+"| "-" | "*" | "/") "=" expr

    function : "function" base_symbol "(" [base_symbol ("," base_symbol)*] ")" block
    fcall : base_symbol "(" [expr ("," expr)*] ")"

    array_op : array_set | array_get
    array_get : base_symbol "[" (INT | string | symbol) ("," (INT | string | symbol))* "]"
    array_set : base_symbol "[" (INT | string | symbol) ("," (INT | string | symbol))* "]" "=" expr

    in_scope : "scope" "(" (symbol | list | fcall) ")" expr
    in_group : "group" "(" (list | fcall | expr) ")" expr

    _NL: /(\r?\n)+\s*/
    statement : [expr ("," expr)* ":"] block
    line : function | statement
    program : [line (_NL line)*]

    COMMENT: /\/\/[^\n]*/

    string : ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_INT
    %import common.INT
    %import common.WORD
    %import common.WS_INLINE
    %import common.WS
    %import common.LETTER
    %import common.NEWLINE
    //%ignore WS_INLINE
    %ignore WS
    %ignore COMMENT
    """

class TreeToWal(Transformer):
    '''Transforms a parsed tree into WAL data structures'''

    function = lambda self, f: Statement([S('BEGIN')], [Op.DEFUN, f[0], f[1:-1], f[-1]])
    statement = lambda self, s: Statement(s[:-1], s[-1])
    line = lambda self, l: l[0]
    program = lambda self, p: p

    string = lambda self, s: s[0][1:-1].encode('utf-8').decode('unicode_escape')
    number = lambda self, n: int(n[0])
    simple_symbol = lambda self, s: s[0]
    symbol = lambda self, s: s[0]
    base_symbol = lambda self, s: S(''.join(list(map(lambda x: x.value, s))))
    scoped_symbol = lambda self, s: [Op.SCOPED, s[0]]
    grouped_symbol = lambda self, s: [Op.RESOLVE_GROUP, s[0]]
    timed_symbol = lambda self, s: [Op.REL_EVAL, s[0], self.number([s[1].value])]
    bit_symbol = lambda self, s: [Op.SLICE, s[0], self.number(s[1].value)]
    sliced_symbol = lambda self, s: [Op.SLICE, s[0], self.number(s[1].value), self.number(s[2].value)]
    block = lambda self, b: [Op.DO] + b
    assign = lambda self, s: s[0]
    assign_std = lambda self, a: [Op.SET, [a[0], a[1]]]
    assign_arith = lambda self, a: [Op.SET, [a[0], [Op(a[1]), a[0], a[3]]]]
    forin = lambda self, f: [Op.MAP, [Op.LAMBDA, [f[0]], f[2]], f[1]]
    forinarray = lambda self, f: [Op.MAPA, [Op.LAMBDA, [f[0], f[1]], f[3]], f[2]]
    #forvar = lambda self, f: [Op.DO, f[0], [Op.WHILE, f[1], [Op.DO, f[3], f[2]]]]

    def forvar(self, f):
        return [Op.LET, f[0][1], [Op.WHILE, f[1], [Op.DO, f[3], f[2]]]]
    #forvar = lambda self, f: [Op.LET, [f[0], [Op.WHILE, f[1], [Op.DO, f[3], f[2]]]]

    array_op = lambda self, a: a[0]
    array_get = lambda self, a: [Op.GETA] + a
    array_set = lambda self, a: [Op.SETA] + a
    cond = lambda self, c: c[0]
    ifstmt = lambda self, c: [Op.IF] + c
    in_scope = lambda self, s: [Op.SCOPED, s[0], s[1]]
    in_group = lambda self, g: [Op.IN_GROUPS, g[0], g[1]]

    list = lambda self, l: [Op.LIST] + l
    #pair = tuple
    #dict = dict
    forstmt = lambda self, f: f[0]
    null = lambda self, _: None
    true = lambda self, _: True
    false = lambda self, _: False

    def fcall(self, f):
        try:
            expr = [Op(f[0].name)] + f[1:]
        except: # pylint: disable=W0702
            expr = [f[0]] + f[1:]
        return expr

    def arith(self, x):
        if len(x) == 2:
            return [Op(x[0].children[0].value), x[1]]
        # convert == to =
        if x[1].children[0].value == '==':
            return [Op.EQ, x[0], x[2]]

        return [Op(x[1].children[0].value), x[0], x[2]]

def parse_wawk(code):
    json_parser = Lark(WAWK_GRAMMAR, start='program')
    parsed = json_parser.parse(code)
    return TreeToWal().transform(parsed)

def test():
    json_parser = Lark(WAWK_GRAMMAR, start='expr')
    parsed = json_parser.parse('group (groups("ready", "valid")) {x}')
    print(TreeToWal().transform(parsed))
