'''Definitions for the wal-awk AST'''

from dataclasses import dataclass
from wal.ast_defs import Symbol as S, Symbol, Operator


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
        wal = self.begin
        main_loop = [Operator.WHENEVER, True, [S('cond'), *[[[Operator.AND, *stmt.condition], stmt.action] for stmt in self.statements]]]
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
