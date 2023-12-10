'''Definitions for the wal-awk AST'''

from dataclasses import dataclass
from wal.ast_defs import Symbol as S, Symbol, Operator, WList


@dataclass
class Statement:
    '''Statement class'''
    condition: []
    action: []


@dataclass
class AST:
    '''Abstract syntax tree.
       Contains definitions of functions and statements'''

    def __init__(self, parsed, trace):
        self.functions = {}
        self.statements = []
        self.begin = []
        self.end = []

        for statement in parsed:
            if statement.condition == [S('BEGIN')]:
                self.begin.append(statement.action)
            elif statement.condition == [S('END')]:
                self.end.append(statement.action)
            elif (statement.condition == [True]
                  and isinstance(statement.action, list)
                  and statement.action[0] == Operator.DEFUN):
                self.begin.append(statement.action)
            else:
                self.statements.append(statement)

    def emit(self):
        main_loop = [Operator.WHENEVER, True]
        for stmt in self.statements:
            main_loop.append([S('when'), [Operator.AND, *stmt.condition], stmt.action])

        variables = self.find_variables(self.begin)
        variables = self.find_variables(self.end, vars=variables)
        variables = self.find_variables(main_loop, vars=variables)

        variable_definitions = [[Operator.DEFINE, S(key[0]), key[1]] for key in variables.items()]
        begin_statements = self.begin
        wal = [[Operator.DO, *variable_definitions, *begin_statements]]
        wal.append(main_loop)
        wal += self.end

        symbols = []
        def find_symbols(expr):
            if isinstance(expr, Symbol):
                symbols.append(expr.name)
            elif isinstance(expr, list):
                for sub in expr:
                    find_symbols(sub)

        find_symbols(wal)
        
        return wal, symbols

    def find_variables(self, expr, vars={}):
        if isinstance(expr, (WList, list)):
            if len(expr) > 1 and expr[0] == Operator.SET:
                for binding in expr[1:]:
                    vars[binding[0].name] = 0
                    self.find_variables(binding[1], vars)
            if len(expr) > 1 and expr[0] == Operator.SETA:
                vars[expr[1].name] = [Operator.ARRAY]
                self.find_variables(expr[-1], vars)
            else:
                for sub_expr in expr:
                    self.find_variables(sub_expr, vars)

        return vars
