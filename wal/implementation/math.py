'''Implementations of math functions'''
# pylint: disable=C0116
import math
import operator

from functools import reduce
from wal.ast_defs import Operator, WList


def op_add(seval, args):
    evaluated = seval.eval_args(args)
    if any(map(lambda x: isinstance(x, (WList, list)), evaluated)):
        res = []
        for item in evaluated:
            if isinstance(item, (WList, list)):
                res += item
            else:
                res.append(item)
    elif any(map(lambda x: isinstance(x, str), evaluated)):
        res = ''.join(map(str, evaluated))
    else:
        res = sum(evaluated)
    return res


def op_sub(seval, args):
    evaluated = seval.eval_args(args)
    assert all(map(lambda x: isinstance(x, (int, float)), evaluated))
    if len(evaluated) == 1:
        res = -evaluated[0]
    else:
        res = reduce(operator.__sub__, evaluated)
    return res


def op_mul(seval, args):
    evaluated = seval.eval_args(args)
    assert all(map(lambda x: isinstance(x, (int, float)), evaluated))
    assert len(evaluated) > 1
    return reduce(operator.__mul__, evaluated)


def op_div(seval, args):
    evaluated = seval.eval_args(args)
    assert all(map(lambda x: isinstance(x, (int, float)), evaluated))
    assert len(evaluated) == 2
    assert evaluated[1] != 0, 'div: division by zero'
    return evaluated[0] / evaluated[1]


def op_exp(seval, args):
    evaluated = seval.eval_args(args)
    assert all(map(lambda x: isinstance(x, (int, float)), evaluated))
    assert len(evaluated) == 2
    return int(math.pow(evaluated[0], evaluated[1]))


def op_floor(seval, args):
    assert len(args) == 1, 'floor: expects exactly one argument (floor x:num?)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (int, float)), 'floor: expects exactly one argument (floor x:num?)'
    return math.floor(evaluated)


def op_ceil(seval, args):
    assert len(args) == 1, 'floor: expects exactly one argument (ceil x:num?)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (int, float)), 'ceil: expects exactly one argument (ceil x:num?)'
    return math.ceil(evaluated)


def op_round(seval, args):
    assert len(args) == 1, 'round: expects exactly one argument (round x:num?)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (int, float)), 'round: expects exactly one argument (round x:num?)'
    return round(evaluated)


def op_mod(seval, args):
    assert len(args) == 2, 'mod: expects exactly one argument (mod x:num?)'
    evaluated = seval.eval_args(args)
    assert all(map(lambda x: isinstance(x, (int, float)), evaluated)), 'mod: expects exactly one argument (mod x:num? y:num?)'
    return evaluated[0] % evaluated[1]


math_operators = {
    Operator.ADD.value: op_add,
    Operator.SUB.value: op_sub,
    Operator.MUL.value: op_mul,
    Operator.DIV.value: op_div,
    Operator.EXP.value: op_exp,
    Operator.FLOOR.value: op_floor,
    Operator.CEIL.value: op_ceil,
    Operator.ROUND.value: op_round,
    Operator.MOD.value: op_mod,
}
