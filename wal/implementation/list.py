from wal.ast_defs import Operator, Symbol

def op_list(seval, args):
    return seval.eval_args(args)


def op_first(seval, args):
    assert len(args) == 1, f'first: expects one argument (first list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, list), f'first: argument must be a list'
    assert evaluated, f'first: argument must have length > 0'
    return evaluated[0]


def op_second(seval, args):
    assert len(args) == 1, f'second: expects one argument (second list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, list), f'second: argument must be a list'
    assert len(evaluated) > 1, f'second: argument must have length > 1'
    return evaluated[1]


def op_last(seval, args):
    assert len(args) == 1, f'last: expects one argument (last list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, list), f'last: argument must be a list'
    assert evaluated, f'last: argument must have length > 0'
    return evaluated[-1]


def op_rest(seval, args):
    assert len(args) == 1, f'rest: expects one argument (rest list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, list), f'rest: argument must be a list'
    return evaluated[1:] if len(evaluated) > 1 else []


def op_in(seval, args):
    assert len(args) >= 2, 'in: expects at least 2 arguments (in value [list|array])'
    evaluated = seval.eval_args(args)
    assert isinstance(evaluated[-1], (list, dict)), 'in: expects list or array as last argument'
    res = True
    if isinstance(evaluated[-1], list):
        for check in evaluated[:-1]:
            if check not in evaluated[-1]:
                res = False
                break
    elif isinstance(evaluated[-1], dict):
        key = '-'.join(map(str, evaluated[:-1]))
        res = key in evaluated[-1]
    return res


def op_map(seval, args):
    assert len(args) == 2, 'map: expects two arguments'

    arg = seval.eval(args[1])
    assert isinstance(arg, list), 'map: second argument must be a list'
    res = []

    if isinstance(args[0], Operator):
        for element in arg:
            res.append(seval.eval([args[0], [Operator.QUOTE, element]]))
    else:
        func = seval.eval(args[0])
        assert func[0] == Operator.LAMBDA, 'map: first argument must be a function'
        for element in arg:
            res.append(seval.eval_lambda(func, [[Operator.QUOTE, element]]))
    return res


def op_zip(seval, args):
    assert len(args) == 2, 'zip: expects two arguments (zip list list)'
    evaluated = seval.eval_args(args)
    return list(map(list, zip(evaluated[0], evaluated[1])))


def op_max(seval, args):
    assert len(args) == 1, 'max: expects one argument (max list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, list), 'max: argument must be a list'
    return max(evaluated)


def op_min(seval, args):
    assert len(args) == 1, 'min: expects one argument (min list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, list), 'min: argument must be a list'
    return min(evaluated)


def op_sum(seval, args):
    assert len(args) == 1, 'sum: expects one argument (min list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, list), 'sum: argument must be a list'
    return sum(evaluated)


def op_average(seval, args):
    assert len(args) == 1, 'average: expects one argument (min list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, list), 'average: argument must be a list'
    return sum(evaluated) / len(evaluated)


def op_length(seval, args):
    assert len(args) == 1, 'length: expects one argument (length list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (list, str)), 'length: argument must be a list'
    return len(evaluated)


def op_fold(seval, args):
    assert len(args) == 3, 'fold: expects 3 arguments (fold f acc data:list)'
    evaluated = seval.eval_args(args[1:])
    assert isinstance(evaluated[-1], list), f'fold: last argument must be a list not {type(evaluated[-1])}'

    acc = evaluated[0]
    if isinstance(args[0], Operator):
        for element in evaluated[1]:
            acc = seval.eval([args[0], [Operator.QUOTE, acc], [Operator.QUOTE, element]])
    else:
        func = seval.eval(args[0])
        assert func[0] == Operator.LAMBDA, 'fold: first argument must be a function'
        for element in evaluated[1]:
            acc = seval.eval_lambda(func, [[Operator.QUOTE, acc], [Operator.QUOTE, element]])

    return acc


def op_range(seval, args):
    assert len(args) >= 1 and len(args) <= 3, 'range: expects one or two arguments (range start:int end:int step:int)'
    evaluated = seval.eval_args(args)
    assert all(isinstance(e, int) for e in evaluated), 'range: all arguments must be ints'

    return list(range(*evaluated))


def op_is_list(seval, args):
    assert len(args) == 1, 'list?: expects exactly one argument (list? list)'
    return isinstance(seval.eval(args[0]), list)


def op_for(seval, args):
    assert len(args) > 1, 'for: expects at least two arguments (for [id:symbol seq:list] body+)'
    assert isinstance(args[0], list), 'for: first argument must be a tuple like [id:symbol seq:list]'
    assert len(args[0]) == 2,  'for: first argument must be a tuple like [id:symbol seq:list]'
    sym = args[0][0]
    sequence = seval.eval(args[0][1])
    assert isinstance(sequence, list), 'for: seq in [id:symbol seq:list] must be a list'
    for v in sequence:
        if seval.stack: # if in a function
            seval.stack[-1][sym.name] = v
            seval.eval_args(args[1:])
            del seval.stack[-1][sym.name]
        else:
            seval.context[sym.name] = v
            seval.eval_args(args[1:])
            del seval.context[sym.name]


list_operators = {
    Operator.LIST.value: op_list,
    Operator.FIRST.value: op_first,
    Operator.SECOND.value: op_second,
    Operator.LAST.value: op_last,
    Operator.REST.value: op_rest,
    Operator.IN.value: op_in,
    Operator.MAP.value: op_map,
    Operator.MAX.value: op_max,
    Operator.MIN.value: op_min,
    Operator.SUM.value: op_sum,
    Operator.AVERAGE.value: op_average,
    Operator.ZIP.value: op_zip,
    Operator.LENGTH.value: op_length,
    Operator.FOLD.value: op_fold,
    Operator.RANGE.value: op_range,
    Operator.IS_LIST.value: op_is_list,
    Operator.FOR.value: op_for
}
