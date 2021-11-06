'''Parsers for wal programs.'''

from parsy import (generate, regex, string, letter, peek,
                   decimal_digit, from_enum, whitespace, ParseError)
from wal.ast import Operator, Symbol, ExpandGroup
from wal.trace import Trace

# pylint: disable=invalid-name

comment = regex(r';.*(\n|$)')
ignore = (whitespace | comment).many()


def lexeme(p):
    '''embed parser in whitespace'''
    return p << ignore


lparen = lexeme(string('('))
rparen = lexeme(string(')'))
boolean = lexeme(string('#t') | string('#f')).map(
    lambda val: 1 if val == '#t' else 0)
binary = lexeme(string('b') >> regex('[01]+')).map(lambda val: int(val, 2))
decimal = lexeme(regex(r'-?\d+')).map(int)
hexadecimal = lexeme(string('0x') >> regex(
    '[0-9a-fA-F]+')).map(lambda val: int(val, 16))
number = binary | decimal | hexadecimal
symbol_base = ((letter | string('_')) +
               (letter | decimal_digit | string('_') |
                string('-') | string('$') | string('.') | string(Trace.SCOPE_SEPERATOR))
               .many().concat()).map(Symbol)

scoped_symbol = lexeme(string('~') >> symbol_base).map(lambda sym: [Operator.RESOLVE_SCOPE, sym])
grouped_symbol = lexeme(string('#') >> symbol_base).map(lambda sym: [Operator.RESOLVE_GROUP, sym])

# @generate
# def timed_symbol():
#     '''Parse a symbol with relative timed acces. Return equivalent function call'''
#     sym = yield symbol_base | scoped_symbol | grouped_symbol
#     time = yield string("@") >> decimal
#     return [Operator.REL_EVAL, sym, time]


# @generate
# def timed_group_expand():
#     '''Parse a symbol with relaive timed group. Expand into multiple expressions'''
#     sym = yield symbol_base | scoped_symbol | grouped_symbol
#     times = yield string("@") >> slist
#     expr = ExpandGroup([[Operator.REL_EVAL, sym, time] for time in times])
#     return expr


symbol = lexeme(scoped_symbol | grouped_symbol | symbol_base)


def unescape(x):
    '''Unescape characters in parsed string'''
    return x.encode('utf-8').decode('unicode_escape')


text = lexeme(string('"') >> regex(
    r'(?:[^"\\]|\\.)*') << string('"')).map(unescape)
# TO hier anstat symbol function
func = lexeme(from_enum(Operator) << peek(whitespace | string(')')))


@generate
def slist():
    '''parse s-expression lists'''
    yield lparen
    sexprs = yield sexpr.many()
    yield rparen
    return sexprs


atom = boolean | number | func | text | symbol
sexpr_unquoted = slist | atom


@generate
def sexpr_quoted():
    '''parse a quoted s-expression'''
    yield string('\'')
    sexpr_u = yield sexpr_unquoted
    return [Operator.QUOTE, sexpr_u]


sexpr_base = ignore >> (sexpr_quoted | sexpr_unquoted)

@generate
def sexpr_rel():
    '''Parse a sexpr followed by a relative evaluation operator'''
    yield ignore
    expr = yield sexpr_base
    time = yield string("@") >> decimal
    return [Operator.REL_EVAL, expr, time]

@generate
def sexpr_rel_group():
    '''Parse a sexpr followed by a group relative evaluation operator'''
    yield ignore
    expr = yield sexpr_base
    times = yield string("@") >> slist
    return ExpandGroup([[Operator.REL_EVAL, expr, time] for time in times])

sexpr = sexpr_rel_group | sexpr_rel | sexpr_base

def parse_sexpr(txt):
    '''Wrappper function for parsing sexprs and basic error output'''
    try:
        return sexpr.parse(txt)
    except ParseError as pe:
        print(txt, pe.index, txt[pe.index])
        print(f'Syntax error: unexpected {txt[pe.index]} at {pe.line_info()}')
    return None
