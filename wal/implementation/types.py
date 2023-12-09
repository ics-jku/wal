'''Implementations for type related functions such as type checking'''
from wal.ast_defs import Operator, Symbol, WList


def op_is_defined(seval, args):
    '''Returns true if the argument is a defined symbol'''
    assert len(args) == 1, 'defined?: expects exactly one argument'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, Symbol), 'defined?: argument must evaluate to symbol'
    return bool(seval.environment.is_defined(evaluated.name))


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
    return all(isinstance(arg, (WList, list)) for arg in evaluated)


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


def op_bits_to_sint(seval, args):
    '''Converts a string to a signed integer '''
    assert len(args) == 1, 'bits->sint: expects exactly one argument (bits->sint expr:str)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, str), 'bits->sint: argument must evaluate to srting'

    if evaluated[0] == '1':
        u_res = int(''.join('1' if x == '0' else '0' for x in evaluated), 2) + 1
        return -u_res

    return int(evaluated, 2)


def op_symbol_to_string(seval, args):
    '''Converts a symbol a to a string "a" '''
    assert len(args) == 1, 'symbol->string: expects exactly one argument (symbol->string expr:symbol)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, Symbol), 'symbol->string: argument must evaluate to symbol'
    return evaluated.name


def op_string_to_symbol(seval, args):
    '''Converts a string to a symbol'''
    assert len(args) == 1, 'string->symbol: expects exactly one argument (string->symbol expr:symbol)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, str), 'symbol->string: argument must evaluate to symbol'
    return Symbol(evaluated)


def op_int_to_string(seval, args):
    '''Converts an integer to its string representation'''
    assert len(args) == 1, 'int->string: expects exactly one argument (symbol->string expr:symbol)'
    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, int), 'int->string: argument must evaluate to symbol'
    return str(evaluated)


type_operators = {
    Operator.IS_DEFINED.value: op_is_defined,
    Operator.IS_ATOM.value: op_is_atom,
    Operator.IS_SYMBOL.value: op_is_symbol,
    Operator.IS_STRING.value: op_is_string,
    Operator.IS_INT.value: op_is_int,
    Operator.IS_LIST.value: op_is_list,
    Operator.CONVERT_BINARY.value: op_convert_binary,
    Operator.STRING_TO_INT.value: op_string_to_int,
    Operator.BITS_TO_SINT.value: op_bits_to_sint,
    Operator.STRING_TO_SYMBOL.value: op_string_to_symbol,
    Operator.SYMBOL_TO_STRING.value: op_symbol_to_string,
    Operator.INT_TO_STRING.value: op_int_to_string,
}
