'''Definitions for the wal-awk AST'''

from dataclasses import dataclass
from wal.ast_defs import S, Operator

@dataclass
class Statement:
    '''Statement class'''
    condition: []
    action: []


@dataclass
class AST:
    '''Abstract syntax tree.
       Contains definitions of functions and statements'''

    def __init__(self, parsed):
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
