'''Implementations for all list related functions'''
from wal.ast_defs import Operator, Symbol, Closure, WList

def op_list(seval, args):
    '''Constructs a new list filled with evaluated arguments'''
    return WList(seval.eval_args(args))


def op_first(seval, args):
    '''Returns the first element of list'''
    assert len(args) == 1, 'first: expects one argument (first list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (WList, list)), f'first: argument must be a list but is {type(evaluated)}'
    assert evaluated, 'first: argument must have length > 0'
    return evaluated[0]


def op_second(seval, args):
    '''Returns the second element of list'''
    assert len(args) == 1, 'second: expects one argument (second list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (WList, list)), 'second: argument must be a list'
    assert len(evaluated) > 1, 'second: argument must have length > 1'
    return evaluated[1]


def op_last(seval, args):
    '''Returns the last element of list'''
    assert len(args) == 1, 'last: expects one argument (last list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (WList, list)), 'last: argument must be a list'
    assert evaluated, 'last: argument must have length > 0'
    return evaluated[-1]


def op_rest(seval, args):
    '''Returns all elements but the first one from list'''
    assert len(args) == 1, 'rest: expects one argument (rest list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (WList, list)), 'rest: argument must be a list'
    return evaluated[1:] if len(evaluated) > 1 else []


def op_in(seval, args):
    '''Returns true if value is contained in list or array'''
    assert len(args) >= 2, 'in: expects at least 2 arguments (in value [list|array])'
    evaluated = seval.eval_args(args)
    assert isinstance(evaluated[-1], (WList, list, dict)), 'in: expects list or array as last argument'
    res = True
    if isinstance(evaluated[-1], (WList, list)):
        for check in evaluated[:-1]:
            if check not in evaluated[-1]:
                res = False
                break
    elif isinstance(evaluated[-1], dict):
        key = '-'.join(map(lambda x: x.name if isinstance(x, Symbol) else str(x), evaluated[:-1]))
        res = key in evaluated[-1]
    return res


def op_map(seval, args):
    '''Applies function to each element of list. Functions must expect exactly one argument.'''
    assert len(args) == 2, 'map: expects two arguments (map function list)'

    arg = seval.eval(args[1])
    assert isinstance(arg, (WList, list)), 'map: second argument must be a list'
    res = []

    if isinstance(args[0], Operator):
        for element in arg:
            res.append(seval.eval(WList([args[0], WList([Operator.QUOTE, element])])))
    else:
        func = seval.eval(args[0])
        assert isinstance(func, Closure), 'map: first argument must be a function'
        for element in arg:
            res.append(seval.eval_closure(func, [[Operator.QUOTE, element]]))

    return res


def op_zip(seval, args):
    '''Combines two lists (a b c) (1 2 3) to ((a 1) (b 2) (c 3))'''
    assert len(args) == 2, 'zip: expects two arguments (zip list list)'
    evaluated = seval.eval_args(args)
    return list(map(list, zip(evaluated[0], evaluated[1])))


def op_max(seval, args):
    '''Returns the largest number from the list'''
    assert len(args) == 1, 'max: expects one argument (max list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (WList, list)), 'max: argument must be a list'
    return max(evaluated)


def op_min(seval, args):
    '''Returns the smalles number from the list'''
    assert len(args) == 1, 'min: expects one argument (min list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (WList, list)), 'min: argument must be a list'
    return min(evaluated)


def op_average(seval, args):
    '''Returns the average from the list'''
    assert len(args) == 1, 'average: expects one argument (min list)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (WList, list)), 'average: argument must be a list'
    return sum(evaluated) / len(evaluated)


def op_length(seval, args):
    '''Returns the length of list'''
    assert len(args) == 1, 'length: expects one argument (length list), {args[0].line_info}'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (WList, list, str, dict)), 'length: argument must be a list'
    return len(evaluated)


def op_fold(seval, args):
    '''Performs a fold left on list with function f'''
    assert len(args) == 3, 'fold: expects 3 arguments (fold f acc data:list)'
    evaluated = seval.eval_args(args[1:])
    assert isinstance(evaluated[-1], (WList, list)), f'fold: last argument must be a list not {type(evaluated[-1])}'

    acc = evaluated[0]
    if isinstance(args[0], Operator):
        for element in evaluated[1]:
            acc = seval.eval(WList([args[0], WList([Operator.QUOTE, acc]), WList([Operator.QUOTE, element])]))
    else:
        func = seval.eval(args[0])
        assert isinstance(func, Closure), 'fold: first argument must be a function'
        for element in evaluated[1]:
            acc = seval.eval_closure(func, WList([WList([Operator.QUOTE, acc]), WList([Operator.QUOTE, element])]))

    return acc


def op_range(seval, args):
    '''Returns a list filled with numbers from arg0 to arg1. Arg1 can be omitted which
    results in a list 0..arg0'''
    assert len(args) >= 1 and len(args) <= 3, 'range: expects one or two arguments (range start:int end:int step:int)'
    evaluated = seval.eval_args(args)
    assert all(isinstance(e, int) for e in evaluated), 'range: all arguments must be ints'
    return list(range(*evaluated))


def op_for(seval, args):
    '''Loops over each element in seq, binds it to id and evaluates the body'''
    assert len(args) > 1, 'for: expects at least two arguments (for [id:symbol seq:list] body+)'
    assert isinstance(args[0], (WList, list)), 'for: first argument must be a tuple like [id:symbol seq:list]'
    assert len(args[0]) == 2,  'for: first argument must be a tuple like [id:symbol seq:list]'
    sym = args[0][0]
    sequence = seval.eval(args[0][1])
    assert isinstance(sequence, (WList, list, str)), 'for: seq in [id:symbol seq:list] must be a list'
    seval.environment.define(sym.name, 0)
    for value in sequence:
        seval.environment.write(sym.name, value)
        seval.eval_args(args[1:])


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
    Operator.AVERAGE.value: op_average,
    Operator.ZIP.value: op_zip,
    Operator.LENGTH.value: op_length,
    Operator.FOLD.value: op_fold,
    Operator.RANGE.value: op_range,
}
