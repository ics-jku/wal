'''Implementations of math functions'''
# pylint: disable=C0116
import operator

from functools import reduce
from wal.ast_defs import Operator


def op_bor(seval, args):
    evaluated = seval.eval_args(args)
    assert all(map(lambda x: isinstance(x, (int)), evaluated))
    if len(evaluated) == 1:
        res = evaluated[0]
    else:
        res = reduce(operator.__or__, evaluated)
    return res

def op_band(seval, args):
    evaluated = seval.eval_args(args)
    assert all(map(lambda x: isinstance(x, (int)), evaluated))
    if len(evaluated) == 1:
        res = evaluated[0]
    else:
        res = reduce(operator.__and__, evaluated)
    return res

def op_bxor(seval, args):
    evaluated = seval.eval_args(args)
    assert all(map(lambda x: isinstance(x, (int)), evaluated))
    if len(evaluated) == 1:
        res = evaluated[0]
    else:
        res = reduce(operator.__xor__, evaluated)
    return res

bitwise_operators = {
    Operator.BOR.value: op_bor,
    Operator.BAND.value: op_band,
    Operator.BXOR.value: op_bxor,
}
