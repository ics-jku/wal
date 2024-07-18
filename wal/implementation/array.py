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
    assert len(args) == 3, 'seta: requires three arguments. (seta array key:(int, str, symbol) value)'
    array = seval.eval(args[0])
    assert isinstance(array, dict), 'seta: must be applied on array'
    key = seval.eval(args[1])
    assert isinstance(key, (int, str, Symbol)), 'seta: key must be either int, string or a symbol'
    val = seval.eval(args[2])
    key = to_str(key)
    array[key] = val
    return array


def op_geta(seval, args):
    '''Returns the value at key from array.'''
    assert len(args) == 2, 'geta: requires at least three arguments. (geta array:(array, symbol) key:(int, str, symbol)'
    array = seval.eval(args[0])
    assert(isinstance(array, dict)), 'geta: first argument must be an array'
    key = seval.eval(args[1])
    assert isinstance(key, (int, str, Symbol)), 'geta: key must be either int, string or a symbol'
    key = to_str(key)

    assert key in array, f'geta: key {key} not found'
    return array[key]


def op_dela(seval, args):
    '''Removes the value at key from array
    Returns the array without the removed value'''
    assert len(args) == 2, 'dela: requires at least two arguments. (dela array key)'
    array = seval.eval(args[0])
    assert(isinstance(array, dict)), 'dela: first argument must be an array'
    key = seval.eval(args[1])
    assert isinstance(key, (int, str, Symbol)), 'geta: key must be either int, string or a symbol'
    key = to_str(key)
    assert key in array, f'dela: key {key} not found'
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
    Operator.DELA.value: op_dela,
    Operator.MAPA.value: op_mapa
}
