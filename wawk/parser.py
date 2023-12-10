'''Parsers for WAWK'''
# pylint: disable=C0103,C0116
from lark import Lark, Transformer
from wawk.ast_defs import Statement
from wal.ast_defs import Symbol as S
from wal.ast_defs import Operator as Op
from wal.reader import operators

WAWK_GRAMMAR = r"""
    ?expr: symbol
         | fcall
         | array_get
         | "(" expr ")"
         | string
         | list
         | neg
         | sum_s
         | or_s
         | SIGNED_INT -> number
         | INT -> number

    line_expr: assign
         | array_set

    block_expr: forstmt
         | cond
         | in_scope
         | in_group

    substatement: (subline | block_expr | block) ";"*
    subline: (line_expr | expr) ";"

    list : "[" [expr ("," expr)*] "]"

    forstmt: forin | forinarray | forvar
    forin: "for" "(" base_symbol "in" (list | fcall | base_symbol) ")" substatement
    forinarray: "for" "(" base_symbol "," base_symbol "in" (fcall | base_symbol) ")" substatement
    forvar: "for" "(" assign_std ";" expr ";" expr  ")" substatement

    cond : ifstmt
    ifstmt : "if" "(" expr ")" substatement ("else" substatement)?

    symbol : simple_symbol | sliced_symbol | bit_symbol
    simple_symbol : base_symbol | scoped_symbol | grouped_symbol | timed_symbol | bit_symbol | sliced_symbol
    scoped_symbol : "~" base_symbol
    grouped_symbol : "#" base_symbol
    timed_symbol : base_symbol "@" SIGNED_INT
    !base_symbol : (LETTER | "_") (LETTER | INT | "_" | "$" | ".")*
    bit_symbol : simple_symbol "[" INT "]"
    sliced_symbol : simple_symbol "[" INT ":" INT "]"

    neg.6 : a_neg | expr
    a_neg.6 : u_op expr

    sum_s.5: a_sum_s | mul
    a_sum_s.5: sum_s a_s_op sum_s
    mul.4: a_mul | expr
    a_mul.4: mul m_d_op mul

    or_s.3: a_or_s | and_s
    a_or_s.3: or_s or_op or_s
    and_s.2: a_and_s | comp
    a_and_s.2: and_s and_op and_s
    comp.1: a_comp | expr
    a_comp.1: and_s comp_op and_s

    !u_op : "!"
    !m_d_op : "*" | "/"
    !a_s_op : "+" | "-"
    !comp_op : "==" | "!=" | ">" | "<" | ">=" | "<="
    !and_op : "&&"
    !or_op : "||"

    block : "{" (substatement)* "}"
    assign : assign_arith | assign_std | define
    assign_std : base_symbol "=" expr
    define : "var" base_symbol "=" expr
    !assign_arith : base_symbol ("+"| "-" | "*" | "/") "=" expr

    function : "function" base_symbol "(" [base_symbol ("," base_symbol)*] ")" block
    fcall : base_symbol "(" [expr ("," expr)*] ")"

    array_op : array_set | array_get
    array_get : base_symbol "[" (INT | string | symbol) ("," (INT | string | symbol))* "]"
    array_set : base_symbol "[" (INT | string | symbol) ("," (INT | string | symbol))* "]" "=" expr

    in_scope : "scope" "(" (symbol | list | fcall) ")" substatement
    in_group : "group" "(" (list | fcall | expr) ")" substatement

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
    %ignore WS
    %ignore COMMENT
    """

class TreeToWal(Transformer):
    '''Transforms a parsed tree into WAL data structures'''

    def function(self, f):
        args = f[1:-1] if f[1] else []
        return Statement([S('BEGIN')], [S('defun'), f[0], args, f[-1]])

    statement = lambda self, s: Statement(s[:-1], s[-1])
    line = lambda self, line: line[0]
    program = lambda self, p: p

    substatement = lambda self, s: s[0]
    subline = lambda self, line: line[0]
    block_expr = lambda self, b: b[0]
    line_expr = lambda self, line: line[0]

    string = lambda self, s: s[0][1:-1].encode('utf-8').decode('unicode_escape')
    number = lambda self, n: int(n[0])
    simple_symbol = lambda self, s: s[0]
    symbol = lambda self, s: s[0]
    base_symbol = lambda self, s: S(''.join(list(map(lambda x: x.value, s))))
    scoped_symbol = lambda self, s: [Op.SCOPED, s[0]]
    grouped_symbol = lambda self, s: [Op.RESOLVE_GROUP, s[0]]
    timed_symbol = lambda self, s: [Op.REL_EVAL, s[0], self.number([s[1].value])]
    bit_symbol = lambda self, s: [Op.SLICE, s[0], self.number([s[1].value])]
    sliced_symbol = lambda self, s: [Op.SLICE, s[0], self.number([s[1].value]), self.number([s[2].value])]
    block = lambda self, b: [Op.DO] + b
    assign = lambda self, s: s[0]
    assign_std = lambda self, a: [Op.SET, [a[0], a[1]]]
    define = lambda self, a: [Op.DEFINE, a[0], a[1]]
    assign_arith = lambda self, a: [Op.SET, [a[0], [Op(a[1]), a[0], a[3]]]]
    forin = lambda self, f: [Op.MAP, [Op.LAMBDA, [f[0]], f[2]], f[1]]
    forinarray = lambda self, f: [Op.MAPA, [Op.LAMBDA, [f[0], f[1]], f[3]], f[2]]
    forvar = lambda self, f: [Op.LET, [f[0][1]], [Op.WHILE, f[1], [Op.DO, f[3], f[2]]]]

    neg = lambda self, x: x[0]
    a_neg = lambda self, x: [Op(x[0].children[0].value), x[1]]
    mul = lambda self, x: x[0]
    a_mul = lambda self, x: [Op(x[1].children[0].value), x[0], x[2]]
    sum_s = lambda self, x: x[0]
    a_sum_s = lambda self, x: [Op(x[1].children[0].value), x[0], x[2]]
    and_s = lambda self, x: x[0]
    a_and_s = lambda self, x: [Op(x[1].children[0].value), x[0], x[2]]
    or_s = lambda self, x: x[0]
    a_or_s = lambda self, x: [Op(x[1].children[0].value), x[0], x[2]]
    comp = lambda self, x: x[0]

    array_op = lambda self, a: a[0]
    array_get = lambda self, a: [Op.GETA_DEFAULT, a[0], 0] + a[1:]
    array_set = lambda self, a: [Op.SETA] + a
    cond = lambda self, c: c[0]
    ifstmt = lambda self, c: [Op.IF] + c
    in_scope = lambda self, s: [Op.SCOPED, s[0], s[1]]
    in_group = lambda self, g: [Op.IN_GROUPS, g[0], g[1]]

    def list(self, ls):
        return [Op.LIST] + (ls if ls != [None] else [])

    forstmt = lambda self, f: f[0]
    null = lambda self, _: None
    true = lambda self, _: True
    false = lambda self, _: False

    def fcall(self, f):
        args = f[1:] if f[1:] != [None] else []
        if f[0].name in operators:
            expr = [Op(f[0].name)] + args
        else:
            expr = [f[0]] + args

        return expr

    def a_comp(self, x):
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
