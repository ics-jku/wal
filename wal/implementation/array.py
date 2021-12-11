from wal.ast_defs import Symbol, Operator


def op_array(seval, args):
    res = {}
    for arg in args:
        assert len(arg) == 2, 'array: arguments must be (key:(int, str) sexpr) tuples'
        key = seval.eval(arg[0])
        value = seval.eval(arg[1])
        assert isinstance(key, (int, str)), 'array: key must be either int or str'
        res[key] = value
    return res


def op_seta(seval, args):
    assert len(args) >= 3, 'seta: requires at least three arguments. (seta name [key:(int, str)] value)'
    evaluated_args = seval.eval_args(args[1:-1])
    evaluated_val = seval.eval(args[-1])
    assert all(map(lambda x: isinstance(x, (int, str, Symbol)),
                   evaluated_args)), 'seta: keys must be either int, string or a symbol'
    res = None
    key = '-'.join(map(str, evaluated_args))
    array = seval.eval(args[0])

    assert isinstance(array, dict), 'seta: must be applied on array'
    array[key] = evaluated_val
    res = array
    return res


def op_geta(seval, args):
    assert len(args) >= 2, 'geta: requires at least two arguments. (geta array:(array, symbol) [key:(int, str, symbol])'

    if isinstance(args[0], Symbol):
        if args[0].name in seval.context:
            array = seval.context[args[0].name]
        elif seval.stack and args[0].name in seval.stack[-1]:
            array = seval.stack[-1][args[0].name]
        else:
            raise ValueError(f'geta: array {args[0].name} not found')
    else:
        array = seval.eval(args[0])

    assert(isinstance(array, dict)), 'geta: first argument must be either array or symbol'
    evaluated = seval.eval_args(args[1:])
    assert all(map(lambda x: isinstance(x, (int, str, Symbol)),
                   evaluated)), 'geta: keys must be either int or string'
    key = '-'.join(map(str, evaluated))

    if key in array:
        return array[key]
    else:
        array[key] = 0
        return 0


def op_mapa(seval, args):
    assert len(args) == 2, 'mapa: requires two arguments. (mapa function array)'
    func = seval.eval(args[0])
    assert isinstance(func, list) and func[0] == Operator.LAMBDA, 'mapa: first argument must be a function'
    arg = seval.eval(args[1])
    assert isinstance(arg, dict), 'mapa: second argument must be an array'
    res = []
    for key, val in arg.items():
        # set current element
        res.append(seval.eval_lambda(func, [[Operator.QUOTE, key], [Operator.QUOTE, val]]))
    return res


array_operators = {
    Operator.ARRAY.value: op_array,
    Operator.SETA.value: op_seta,
    Operator.GETA.value: op_geta,
    Operator.MAPA.value: op_mapa
}
