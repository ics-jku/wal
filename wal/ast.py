'''Module containing the AST definitions'''
from dataclasses import dataclass
from enum import Enum, unique

@unique
class Operator(Enum):
    '''Enum for built in operations'''
    # waveform
    LOAD = 'load'
    STEP = 'step'
    # basic
    ATOM = 'atom'
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
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
    GET = 'get'
    CALL = 'call'
    IMPORT = 'import'
    LIST = 'list'
    FIRST = 'first'
    SECOND = 'second'
    LAST = 'last'
    REST = 'rest'
    IN = 'in'
    MAP = 'map'
    MAX = 'max'
    MIN = 'min'
    SUM = 'sum'
    LENGTH = 'length'
    AVERAGE = 'average'
    ZIP = 'zip'
    TYPE = 'type'
    GET_AT_TIME = '@'
    REL_EVAL = 'reval'
    ARRAY = 'array'
    SETA = 'seta'
    GETA = 'geta'
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
    # special
    FIND = 'find'
    WHENEVER = 'whenever'
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
