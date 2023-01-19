'''Module containing the AST definitions'''
from dataclasses import dataclass
from enum import Enum, unique

@unique
class Operator(Enum):
    '''Enum for built in operations'''
    # waveform
    LOAD = 'load'
    UNLOAD = 'unload'
    STEP = 'step'
    REPL = 'repl'
    LOADED_TRACES = 'loaded-traces'
    # basic
    REQUIRE = 'require'
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    FDIV = 'fdiv'
    EXP = '**'
    NOT = '!'
    EQ = '='
    NEQ = '!='
    LARGER = '>'
    SMALLER = '<'
    LARGER_EQUAL = '>='
    SMALLER_EQUAL = '<='
    AND = '&&'
    OR = '||'
    PRINT = 'print'
    PRINTF = 'printf'
    SET = 'set'
    LET = 'let'
    LETRET = 'letret'
    INC = 'inc'
    IF = 'if'
    COND = 'cond'
    WHEN = 'when'
    UNLESS = 'unless'
    CASE = 'case'
    WHILE = 'while'
    DO = 'do'
    ALIAS = 'alias'
    UNALIAS = 'unalias'
    QUOTE = 'quote'
    EVAL = 'eval'
    DEFUN = 'defun'
    LAMBDA = 'lambda'
    FN = 'fn'
    GET = 'get'
    CALL = 'call'
    IMPORT = 'import'
    LIST = 'list'
    FOR = 'for'
    FIRST = 'first'
    SECOND = 'second'
    LAST = 'last'
    REST = 'rest'
    IN = 'in'
    MAP = 'map'
    MAX = 'max'
    MIN = 'min'
    SUM = 'sum'
    FOLD = 'fold'
    LENGTH = 'length'
    AVERAGE = 'average'
    ZIP = 'zip'
    RANGE = 'range'
    TYPE = 'type'
    REL_EVAL = 'reval'
    ARRAY = 'array'
    SETA = 'seta'
    GETA = 'geta'
    GETA_DEFAULT = 'geta/default'
    DELA = 'dela'
    MAPA = 'mapa'
    ALLSCOPES = 'all-scopes'
    SCOPED = 'in-scope'
    RESOLVE_SCOPE = 'resolve-scope'
    SETSCOPE = 'set-scope'
    UNSETSCOPE = 'unset-scope'
    GROUPS = 'groups'
    IN_GROUP = 'in-group'
    IN_GROUPS = 'in-groups'
    RESOLVE_GROUP = 'resolve-group'
    SLICE = 'slice'
    # types
    IS_ATOM = 'atom?'
    IS_SYMBOL = 'symbol?'
    IS_STRING = 'string?'
    IS_INT = 'int?'
    IS_LIST = 'list?'
    CONVERT_BINARY = 'convert/bin'
    STRING_TO_INT = 'string->int'
    SYMBOL_TO_STRING = 'symbol->string'
    INT_TO_STRING = 'int->string'
    # special
    FIND = 'find'
    FIND_G = 'find/g'
    WHENEVER = 'whenever'
    FOLD_SIGNAL = 'fold/signal'
    COUNT = 'count'
    TIMEFRAME = 'timeframe'
    SIGNAL_WIDTH = 'signal-width'
    SAMPLE_AT = 'sample-at'
    # system
    EXIT = 'exit'


@dataclass
class Symbol:
    '''Symbol class'''
    name: str

    def __init__(self, name):
        self.name = name


def S(name):  # pylint: disable=C0103
    '''Helper function to create Symbols'''
    return Symbol(name)


# pylint: disable=R0903
class ExpandGroup:
    '''Wrapper for expand groups'''
    def __init__(self, elements):
        self.elements = elements
