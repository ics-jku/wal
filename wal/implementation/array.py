'''Implementations for all array related functions'''

from wal.ast_defs import Symbol, Operator, Closure


def op_array(seval, args):
    '''Creates a new array and populates it with the values passed in args'''
    res = {}
    for arg in args:
        assert len(arg) == 2, 'array: arguments must be (key:(int, str, Symbol) sexpr) tuples'
        key = seval.eval(arg[0])
        assert isinstance(key, (int, str, Symbol)), 'array: keys must be either int, str, or Symbol'

        if isinstance(key, Symbol):
            key = key.name
        elif isinstance(key, int):
            key = str(key)

        value = seval.eval(arg[1])
        res[key] = value
    return res


def to_str (sexpr):
    '''Converts argument sexpr to string. If sexpr is a symbol returns its name'''
    return sexpr.name if isinstance(sexpr, Symbol) else str(sexpr)


def op_seta(seval, args):
    '''Updates values depending on the tuples in args'''
    assert len(args) >= 3, 'seta: requires at least three arguments. (seta name [key:(int, str)] value)'
    evaluated_args = seval.eval_args(args[1:-1])
    evaluated_val = seval.eval(args[-1])
    assert all(map(lambda x: isinstance(x, (int, str, Symbol)),
                   evaluated_args)), 'seta: keys must be either int, string or a symbol'
    res = None
    key = '-'.join(map(to_str, evaluated_args))
    array = seval.eval(args[0])

    assert isinstance(array, dict), 'seta: must be applied on array'
    array[key] = evaluated_val
    res = array
    return res


def op_geta_default(seval, args):
    '''Returns the value from key '-'.join(keys) from array. If key is not in array return default'''
    assert len(args) >= 3, 'geta: requires at least three arguments. (geta array:(array, symbol) default:expr [key:(int, str, symbol])'
    array = seval.eval(args[0])
    assert(isinstance(array, dict)), 'geta: first argument must be either array or symbol'
    evaluated = seval.eval_args(args[2:])
    assert all(map(lambda x: isinstance(x, (int, str, Symbol)),
                   evaluated)), 'geta: keys must be either int or string'

    key = '-'.join(map(to_str, evaluated))
    default = args[1]

    if key in array:
        return array[key]

    if key not in array and default is None:
        raise ValueError(f'Key {key} not found')

    default = seval.eval(default)
    return default


def op_geta(seval, args):
    '''Returns the value from key '-'.join(keys) from array'''
    assert len(args) >= 2, 'geta: requires at least two arguments. (geta array:(array, symbol) [key:(int, str, symbol])'
    return op_geta_default(seval, [args[0], None] + args[1:])


def op_dela(seval, args):
    '''Removes the value from key '-'.join(keys) from array
    Returns the array without the removed value'''
    assert len(args) >= 2, 'dela: requires at least two arguments. (dela array:(array, symbol) [key:(int, str, symbol])'
    array = seval.eval(args[0])
    assert(isinstance(array, dict)), 'dela: first argument must be either array or symbol'
    evaluated = seval.eval_args(args[1:])
    assert all(map(lambda x: isinstance(x, (int, str, Symbol)),
                   evaluated)), 'dela: keys must be either int or string'

    key = '-'.join(map(str, evaluated))
    del array[key]
    return array


def op_mapa(seval, args):
    '''Applies function to every key value pair in array'''
    assert len(args) == 2, 'mapa: requires two arguments. (mapa function array)'
    func = seval.eval(args[0])
    assert isinstance(func, Closure), 'mapa: first argument must be a function'
    arg = seval.eval(args[1])
    assert isinstance(arg, dict), 'mapa: second argument must be an array'
    res = []
    for key, val in arg.items():
        # set current element
        res.append(seval.eval_closure(func, [[Operator.QUOTE, key], [Operator.QUOTE, val]]))
    return res


array_operators = {
    Operator.ARRAY.value: op_array,
    Operator.SETA.value: op_seta,
    Operator.GETA.value: op_geta,
    Operator.GETA_DEFAULT.value: op_geta_default,
    Operator.DELA.value: op_dela,
    Operator.MAPA.value: op_mapa
}
