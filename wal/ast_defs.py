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
    # maths
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    EXP = '**'
    FLOOR = 'floor'
    CEIL = 'ceil'
    ROUND = 'round'
    MOD = 'mod'
    # logic
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
    DEFINE = 'define'
    LET = 'let'
    IF = 'if'
    CASE = 'case'
    WHILE = 'while'
    DO = 'do'
    ALIAS = 'alias'
    UNALIAS = 'unalias'
    QUOTE = 'quote'
    QUASIQUOTE = 'quasiquote'
    UNQUOTE = 'unquote'
    EVAL = 'eval'
    PARSE = 'parse'
    DEFMACRO = 'defmacro'
    MACROEXPAND = 'macroexpand'
    GENSYM = 'gensym'
    LAMBDA = 'lambda'
    FN = 'fn'
    GET = 'get'
    CALL = 'call'
    IMPORT = 'import'
    LIST = 'list'
    # FOR = 'for'
    FIRST = 'first'
    SECOND = 'second'
    LAST = 'last'
    REST = 'rest'
    IN = 'in'
    MAP = 'map'
    MAX = 'max'
    MIN = 'min'
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
    IS_DEFINED = 'defined?'
    IS_ATOM = 'atom?'
    IS_SYMBOL = 'symbol?'
    IS_STRING = 'string?'
    IS_INT = 'int?'
    IS_LIST = 'list?'
    CONVERT_BINARY = 'convert/bin'
    STRING_TO_INT = 'string->int'
    BITS_TO_SINT = 'bits->sint'
    STRING_TO_SYMBOL = 'string->symbol'
    SYMBOL_TO_STRING = 'symbol->string'
    INT_TO_STRING = 'int->string'
    # special
    FIND = 'find'
    FIND_G = 'find/g'
    WHENEVER = 'whenever'
    FOLD_SIGNAL = 'fold/signal'
    SIGNAL_WIDTH = 'signal-width'
    SAMPLE_AT = 'sample-at'
    # system
    EXIT = 'exit'
    # virtual signals
    DEFSIG = 'defsig'
    NEWTRACE = 'new-trace'
    DUMPTRACE = 'dump-trace'


operators = set([op.value for op in Operator])

    
class Symbol:
    '''Symbol class'''

    def __init__(self, name, steps=None):
        self.name = name
        self.steps = steps

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.name == other.name and self.steps == other.steps

        return False


def S(name, steps=None):  # pylint: disable=C0103
    '''Helper function to create Symbols'''
    return Symbol(name, steps)


class UserOperator:
    '''Class that wraps a user specified operator'''

    def __init__(self, name):
        assert name not in operators, f'redefining {name} is not allowed'
        self.name = name


class Environment:
    '''Object that holds a WAL environment '''

    def __init__(self, parent=None):
        self.environment = {}
        self.parent = parent

    def define(self, name, value):
        '''Define new variable in this context '''

        assert name not in self.environment, f'variable {name} already defined'
        self.environment[name] = value

    def undefine(self, name):
        '''Remove definition from this context'''
        assert name in self.environment, f'variable {name} is not defined'
        del self.environment[name]

    def is_defined(self, name):
        '''Check if name is defined somewhere and return that environment'''

        if name in self.environment:
            return self.environment

        if self.parent:
            return self.parent.is_defined(name)

        return False

    def write(self, name, value):
        '''Write to variable name'''

        if name in self.environment:
            self.environment[name] = value
        else:
            assert self.parent
            self.parent.write(name, value)

    def read(self, name):
        '''Read from variable name'''

        if name in self.environment:
            return self.environment[name]

        assert self.parent, f'variable {name} is undefined'
        return self.parent.read(name)



class Closure:
    '''Class implementing a closure '''

    def __init__(self, environment, args, expression, name='lambda'):
        self.name = name
        self.environment = environment
        self.args = args
        self.expression = expression


class Macro:
    '''Class that holds a macro'''

    def __init__(self, name, args, expression):
        self.name = name
        self.args = args
        self.expression = expression


@dataclass
class Unquote:
    '''Utility class for unquote syntax'''
    content: any


@dataclass
class UnquoteSplice:
    '''Utility class for unquote splice syntax'''
    content: any


class VirtualSignal:
    '''Holds information about a virtual signal'''
    name: str


    def __init__(self, name, expr, trace, seval, width=32): # pylint: disable=R0913
        self.name = name
        self.expr = expr
        self.width = width
        self.trace = trace
        self.seval = seval
        self.dependencies = []
        self.cache = {}


    @property
    def value(self):
        '''Returns the value of this virtual signal'''
        index = self.trace.index
        ts = self.trace.timestamps[index]
        if ts in self.cache:
            res = self.cache[ts]
        else:
            res = self.seval.eval_args(self.expr)[-1]
            self.cache[ts] = res


        return res
