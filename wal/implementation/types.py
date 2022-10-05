'''Implementations for type related functions such as type checking'''
from wal.ast_defs import Operator, Symbol


def op_is_atom(seval, args):
    '''Returns true if all arguments evaluate to atoms'''
    evaluated = seval.eval_args(args)
    return all(isinstance(arg, (Operator, Symbol, str, int)) for arg in evaluated)


def op_is_symbol(seval, args):
    '''Returns true if all arguments evaluate to symbols'''
    evaluated = seval.eval_args(args)
    return all(isinstance(arg, Symbol) for arg in evaluated)


def op_is_string(seval, args):
    '''Returns true if all arguments evaluate to strings'''
    evaluated = seval.eval_args(args)
    return all(isinstance(arg, str) for arg in evaluated)


def op_is_int(seval, args):
    '''Returns true if all arguments evaluate to integers'''
    evaluated = seval.eval_args(args)
    return all(isinstance(arg, int) for arg in evaluated)


def op_is_list(seval, args):
    '''Returns true if all arguments evaluate to lists'''
    evaluated = seval.eval_args(args)
    return all(isinstance(arg, list) for arg in evaluated)


def op_convert_binary(seval, args):
    '''Converts an integer to a binray string of width bits'''
    assert len(args) == 1 or len(args) == 2, 'convert/bin: expects at least one argument (convert/bin expr:int width:int)'
    evaluated = seval.eval_args(args)
    value = evaluated[0]
    width = evaluated[1] if len(args) == 2 else 0
    assert isinstance(value, int), 'convert/bin: first argument must evaluate to int'
    assert isinstance(width, int), 'convert/bin: second argument must evaluate to int'
    return f'{value:0{width}b}'.format(value=value, width=width) # pylint: disable=C0116


def op_string_to_int(seval, args):
    '''Converts a string to an integer '''
    assert len(args) == 1 or len(args) == 2, 'string->int: expects exactly one argument (string->int expr:str base:int?)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, str), 'string->int: argument must evaluate to srting'
    if len(args) == 1:
        return int(evaluated)

    assert isinstance(args[1], int), 'string->int: argument base must be integer'
    assert args[1] in [2, 8, 10, 16] , 'string->int: valid base values (2 8 10 16)'
    return int(evaluated, args[1])


def op_symbol_to_string(seval, args):
    '''Converts a symbol a to a string "a" '''
    assert len(args) == 1, 'symbol->string: expects exactly one argument (symbol->string expr:symbol)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, Symbol), 'symbol->string: argument must evaluate to symbol'
    return evaluated.name


def op_int_to_string(seval, args):
    '''Converts an integer to its string representation'''
    assert len(args) == 1, 'int->string: expects exactly one argument (symbol->string expr:symbol)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, int), 'int->string: argument must evaluate to symbol'
    return str(evaluated)


type_operators = {
    Operator.IS_ATOM.value: op_is_atom,
    Operator.IS_SYMBOL.value: op_is_symbol,
    Operator.IS_STRING.value: op_is_string,
    Operator.IS_INT.value: op_is_int,
    Operator.IS_LIST.value: op_is_list,
    Operator.CONVERT_BINARY.value: op_convert_binary,
    Operator.STRING_TO_INT.value: op_string_to_int,
    Operator.SYMBOL_TO_STRING.value: op_symbol_to_string,
    Operator.INT_TO_STRING.value: op_int_to_string,
}
