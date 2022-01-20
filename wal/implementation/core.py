import re
import os
import sys
import math
import operator
import importlib

from functools import reduce, lru_cache
from wal.ast_defs import Operator, Symbol


def op_atom(seval, args):
    evaluated = seval.eval_args(args)
    return all([isinstance(arg, (Operator, Symbol, str, int)) for arg in evaluated])


def op_add(seval, args):
    evaluated = seval.eval_args(args)
    assert len(evaluated) > 1
    if any(map(lambda x: isinstance(x, list), evaluated)):
        res = []
        for item in evaluated:
            if isinstance(item, list):
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
    assert all(map(lambda x: isinstance(x, int), evaluated))
    if len(evaluated) == 1:
        res = -evaluated[0]
    else:
        res = reduce(operator.__sub__, evaluated)
    return res


def op_mul(seval, args):
    evaluated = seval.eval_args(args)
    assert all(map(lambda x: isinstance(x, int), evaluated))
    assert len(evaluated) > 1
    return reduce(operator.__mul__, evaluated)


def op_div(seval, args):
    evaluated = seval.eval_args(args)
    assert all(map(lambda x: isinstance(x, int), evaluated))
    assert len(evaluated) == 2
    if evaluated[1] == 0:
        print('WARNING: division by zero. Is this intended?')
        return None

    return evaluated[0] / evaluated[1]


def op_exp(seval, args):
    evaluated = seval.eval_args(args)
    assert all(map(lambda x: isinstance(x, int), evaluated))
    assert len(evaluated) == 2
    return int(math.pow(evaluated[0], evaluated[1]))


def op_not(seval, args):
    evaluated = seval.eval_args(args)
    assert len(evaluated) >= 1
    assert all(isinstance(arg, int) for arg in evaluated)
    return not any(evaluated)


def op_eq(seval, args):
    evaluated = seval.eval_args(args)
    assert len(evaluated) > 1
    return all(e == evaluated[0] for e in evaluated)


def op_neq(seval, args):
    evaluated = seval.eval_args(args)
    assert len(evaluated) > 1
    return not all(e == evaluated[0] for e in evaluated)


def op_larger(seval, args):
    assert len(args) == 2
    evaluated = seval.eval_args(args)
    assert all(isinstance(arg, int) for arg in evaluated)
    return evaluated[0] > evaluated[1]


def op_smaller(seval, args):
    assert len(args) == 2
    evaluated = seval.eval_args(args)
    assert all(isinstance(arg, int) for arg in evaluated)
    return evaluated[0] < evaluated[1]


def op_larger_equal(seval, args):
    assert len(args) == 2
    evaluated = seval.eval_args(args)
    assert all(isinstance(arg, int) for arg in evaluated)
    return evaluated[0] >= evaluated[1]


def op_smaller_equal(seval, args):
    assert len(args) == 2
    evaluated = seval.eval_args(args)
    assert all(isinstance(arg, int) for arg in evaluated)
    return evaluated[0] <= evaluated[1]


def op_and(seval, args):
    assert len(args) > 0, '&&: expects at least one argument'    
    for arg in args:
        if not seval.eval(arg):
            return False
    return True


def op_or(seval, args):
    assert len(args) > 0, '||: expects at least one argument'
    for arg in args:
        if seval.eval(arg):
            return True
    return False


def op_let(seval, args):
    assert len(args)
    context = seval.context
    if seval.stack:
        context = seval.stack[-1]
    bound = set()

    def unbind():
        for name in bound:
            del context[name]

    try:
        for pair in args[:-1]:
            assert len(pair) == 2, 'let: expects a list of pairs'
            assert isinstance(pair[0], Symbol), 'let: first argument must be a symbol'
            assert pair[0].name not in context, f'let: {pair[0]} already bound'
            context[pair[0].name] = seval.eval(pair[1])
            bound.add(pair[0].name)

        # evaluate body
        res = seval.eval(args[-1])
        unbind()
        return res
    except Exception as e:
        unbind()
        raise e


def op_letret(seval, args):
    assert len(args) == 2, 'letret: expects exactly two parameters (letret def body)'
    context = seval.context
    if seval.stack:
        context = seval.stack[-1]

    pair = args[0]
    assert isinstance(pair, list), 'letret: first argument must be a pair (name def)'
    assert len(pair) == 2, 'letret: first argument must be a pair (name def)'
    assert pair[0].name not in context, f'letret: {pair[0]} already bound'
    context[pair[0].name] = seval.eval(pair[1])
    # eval body
    seval.eval(args[1])
    res = context[pair[0].name]
    del context[pair[0].name]
    return res



def op_set(seval, args):
    assert args, 'set: expects at least one (key:symbol expr) pair'
    for arg in args:
        assert isinstance(arg, list), 'set: arguments must be (key:symbol expr) tuples'
        assert len(arg) == 2, 'set: arguments must be (key:symbol expr) tuples'
        key = arg[0]
        assert isinstance(key, Symbol), 'set: key must be a symbol not'
        res = seval.eval(arg[1])
        if seval.stack: # if in a function
            seval.stack[-1][arg[0].name] = res
        else:
            seval.context[arg[0].name] = res

    return res


def op_inc(seval, args):
    assert args, 'inc expects at least one argument'
    for arg in args:
        if isinstance(arg, Symbol):
            name = arg.name
        else:
            arg = seval.eval(arg)
            assert isinstance(arg, Symbol), 'arguments to inc must be symbols'
            name = arg.name

        if arg.name not in seval.context:
            seval.context[arg.name] = 0

        assert isinstance(seval.context[arg.name], int), 'arguments to inc must be integers'
        res = seval.context[arg.name] = seval.context[arg.name] + 1

    return res


def op_print(seval, args):
    print(*seval.eval_args(args), sep='')
    return None


def op_printf(seval, args):
    assert args, 'printf: expects at least a format string'
    format_evaluated = seval.eval(args[0])
    if isinstance(format_evaluated, str):
        evaluated = seval.eval_args(args[1:])
        print(format_evaluated % tuple(evaluated), sep='', end='')
    else:
        raise ValueError('printf\'s first argument must be a format string')
    return None


def op_if(seval, args):
    assert len(args) == 2 or len(args) == 3, 'if: expects a condition, if-clause and optionally an else-clause'
    if seval.eval(args[0]):
        return seval.eval(args[1])
    else:
        if len(args) == 3:
            return seval.eval(args[2])


def op_cond(seval, args):
    assert args, 'cond: expects a list of clauses (cond (cond1 clause+)+)'
    for clause in args:
        assert isinstance(clause, list), 'cond: clauses must be tuples (cond clause)'
        assert len(clause) >= 2, 'cond: clauses must be tuples (cond clause)'
        if seval.eval(clause[0]):
            return seval.eval_args(clause[1:])[-1]
#            return seval.eval(clause[1])


def op_when(seval, args):
    assert len(args) >= 2, 'when: expects a condition and a clause'
    if seval.eval(args[0]):
        return seval.eval_args(args[1:])[-1]


def op_unless(seval, args):
    assert len(args) >= 2, 'unless: expects a condition and a clause'
    if not seval.eval(args[0]):
        return seval.eval_args(args[1:])[-1]


def op_case(seval, args):
    assert args, 'case: expects at least one case argument'
    res = None
    keyform = seval.eval(args[0])
    clauses = args[1:]
    if len(set(map(lambda x: str(x[0]), clauses))) != len(clauses):
        raise ValueError('case with duplicate key')

    for clause in clauses:
        key = clause[0]
        consequents = clause[1:]
        if keyform == key:
            return seval.eval_args(consequents)[-1]

def op_do(seval, args):
    assert args, 'do: expects at least on argument'
    return seval.eval_args(args)[-1]


def op_while(seval, args):
    assert len(args) >= 2, 'while: expects exactly two arguments (while cond (body:expr))'
    condition = args[0]
    body = args[1:]
    res = None
    while seval.eval(condition):
        res = seval.eval_args(body)[-1]
    return res


def op_alias(seval, args):
    assert args, 'alias: expects at least two arguments'
    assert len(args) % 2 == 0, 'alias: expects an even number of arguments'
    assert isinstance(args[0], Symbol), 'unalias: first argument of pair must be a symbol'
    assert isinstance(args[1], Symbol), 'unalias: second argument of pair must be a symbol'
    for i in range(0, int(len(args) / 2) + 1, 2):
        seval.aliases[args[i].name] = args[i + 1].name


def op_unalias(seval, args):
    assert len(args) == 1, 'unalias: expects exactly one argument'
    assert isinstance(args[0], Symbol), 'unalias: argument must be a symbol'
    assert args[0].name in seval.aliases, f'unalias: no alias {args[0].name} known. Can\'t unalias'
    del seval.aliases[args[0].name]


def op_quote(seval, args):
    assert len(args) == 1, 'quote: expects exactly one argument'
    return args[0]


def op_eval(seval, args):
    assert len(args) == 1, 'eval: expects exactly one argument'
    evaluated = seval.eval(args[0])
    return seval.eval(evaluated)


def op_defun(seval, args):
    assert len(args) >= 3, 'defun: '
    assert isinstance(args[0], Symbol), f'defun: first argument must be a symbol not {args[0]}'
    assert isinstance(args[1], list), 'defun: second argument must be a list of symbols'
    #assert all(isinstance(s, Symbol) for s in args[1]), 'defun: second argument must be a list of symbols'
    assert isinstance(args[2], (Symbol, int, str, list)), 'defun: third argument must be a valid expression'
    seval.context[args[0].name] = [Operator.LAMBDA, args[1], [Operator.DO, *args[2:]]]


def op_lambda(seval, args):
    assert len(args) == 2, 'lambda: expects exactly two arguments (lambda (symbol* | (symbol expr)) sexpr)'
    assert isinstance(args[0], list), 'lambda: first argument must be a list of symbols or symbol expression pairs'
    assert all(isinstance(arg, (list, Symbol)) for arg in args[0])
    return [Operator.LAMBDA, args[0], args[1]]


def op_get(seval, args):
    '''get returns the value of a wavefile signal by its string name'''
    assert len(args) == 1, 'get: expects exactly one argument'
    evaluated = seval.eval_args(args)
    if isinstance(evaluated[0], str):
        return seval.eval(Symbol(evaluated[0]))
    elif isinstance(evaluated[0], Symbol):
        return seval.eval(evaluated[0])


def op_import(seval, args):
    '''Evaluate import operations'''
    assert len(args) >= 1, 'Import expects at least one argument'

    def do_import(name):
        sys.path.append(os.getcwd())
        if isinstance(name, str):
            seval.imports[name] = importlib.import_module(name)
        elif isinstance(name, Symbol):
            seval.imports[name.name] = importlib.import_module(name.name)
        else:
            raise ValueError(
                'Import arguments must be a string or a Symbol, not ' + str(type(name)))

    for arg in args:
        if isinstance(arg, Symbol):
            do_import(arg.name)
        else:
            evaluated = seval.eval({}, arg)
            do_import(evaluated)


def op_call(seval, args):
    '''Evaluate calls to external python modules'''
    extern_name = args[0]
    extern_args = args[1:]
    assert isinstance(extern_name, Symbol)
    module, fname = extern_name.name.split('.')
    func = getattr(seval.imports[module], fname)
    n_args = len(extern_args)
    min_args = func.__code__.co_argcount - len(func.__defaults__) if func.__defaults__ else 0
    max_args = func.__code__.co_argcount
    assert n_args >= min_args <= max_args, f'{extern_name} requires {min_args} to {max_args}'
    evaluated = list(map(lambda x: seval.eval(x), extern_args))
    return func(*evaluated)


def op_type(seval, args):
    return type(seval.eval(args[0]))


def op_rel_eval(seval, args):
    assert len(args) == 2, '@: expects two arguments (@ expr:expr offset:expr->int)'
    assert isinstance(args[0], (Symbol, int, str, list)), '@: first argument must be a valid expression'
    offset = seval.eval(args[1])
    assert isinstance(offset, int), '@: second argument must evaluate to int'
    # check if any trace becomes oob with offset
    for trace in seval.traces.traces.values():
        if trace.index + offset > trace.max_index or trace.index + offset < 0:
            return False

    seval.traces.step(offset)
    res = seval.eval(args[0])
    seval.traces.step(-offset)
    return res


def op_get_at_time_old(seval, args):
    assert len(args) == 2, '@: exactly two arguments required (@ signal:symbol offset:int)'
    # if first arg is not symbol or str eval it
    if not isinstance(args[0], (Symbol, str)):
        args[0] = seval.eval(args[0])
        # first arg must now be either symbol or str
    if isinstance(args[0], Symbol):
        if args[0].name in seval.aliases:
            name = seval.aliases[args[0].name]
        else:
            name = args[0].name
        if args[0].scoped:
            name = seval.scope + '.' + name
        elif isinstance(args[0], str):
            name = args[0]
        else:
            raise ValueError(f'@: first argument must be Symbol or string but is {type(args[0]).__name__}')
        assert isinstance(args[1], int), f'@: second argument must be int but is {type(args[1]).__name__}'

        if seval.traces.contains(name):
            return seval.traces.signal_value(name, args[1])


def op_scoped(seval, args):
    assert len(args) == 2, 'scoped: exactly two arguments required (scoped scope:symbol expression)'
    prev_scope = seval.scope

    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (str, Symbol)), 'scoped: argument must be Symbol, string or must evaluate to one of them'

    if isinstance(evaluated, Symbol):
        name = evaluated.name
    elif isinstance(evaluated, str):
        name = evaluated

    seval.scope = name
    seval.context['CS'] = seval.scope
    res = seval.eval(args[1])
    seval.scope = prev_scope
    seval.context['CS'] = prev_scope
    return res


def op_allscopes(seval, args):
    assert args, 'all-scopes: exactly one argument required'
    assert isinstance(args[0], list), 'all-scopes: argument must be a valid expression'
    res = []
    prev_scope = seval.context['CS']
    for scope in seval.traces.scopes: # pylint: disable=E1101
        seval.scope = scope
        seval.context['CS'] = scope
        res.append(seval.eval(args[0]))
    seval.context['CS'] = prev_scope
    return res


def op_resolve_scope(seval, args):
    assert len(args) == 1, 'resolve-scope: exactly one argument required (resolve-scope name:symbol)'
    assert isinstance(args[0], Symbol), 'resolve-scope: exactly one argument required (resolve-scope name:symbol)'
    if args[0].name in seval.aliases:
        args[0].name = seval.aliases[args[0].name]

    if seval.context['CS'] in seval.traces.scopes:  # if the scope is a real scope add .
        name = seval.context['CS'] + '.' + args[0].name
    else:  # if scope is not a real scope it must be a group name, no dot required
        name = seval.context['CS'] + args[0].name

    if seval.traces.contains(name):
        return seval.traces.signal_value(name)


def op_set_scope(seval, args):
    assert args, 'set-scope: exactly one argument required'
    assert isinstance(args[0], Symbol), f'set-scope: argument must be Symbo but is {type(args[0]).__name__}'
    assert args[0].name in seval.traces.scopes, f'set-scope: {args[0].name} is not a valid scope' # pylint: disable=E1101
    seval.scope = args[0].name
    seval.context['CS'] = args[0].name


def op_unset_scope(seval, args):
    assert not args, 'unset-scope: expects no arguments'
    seval.scope = ''
    seval.context['CS'] = ''


def op_groups(seval, args):
    '''
    (group "*_ready" "*_valid" "*_data") => all signals (as scope?) for which p_ready, p_valid. exist
    '''
    assert args, 'groups: expects at least one argument (groups post:str+)'
    assert all(isinstance(arg, str) for arg in args)

    if seval.context['CS']:
        pattern = re.compile(rf'{seval.context["CS"]}\.[^\\.]+{args[0]}')
    else:
        pattern = re.compile(rf'.*{args[0]}')

    candidates = list(filter(lambda signal: pattern.fullmatch(signal), seval.traces.signals))
    groups = set()
    for pre in candidates:
        pre = pre[:-len(args[0])]  # cut off filter suffix
        if all(seval.traces.contains(f'{pre}{post}') for post in args[1:]):
            groups.add(pre)
    # return list(map(lambda g: [Operator.QUOTE, Symbol(g)], groups))
    return list(groups)


def op_in_group(seval, args):
    assert len(args) == 2, 'in-group: exactly two arguments required (in-group group:symbol expression)'
    prev_group = seval.group
    prev_scope = seval.scope

    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (str, Symbol)), 'in-group: argument must be Symbol, string or must evaluate to one of them'

    if isinstance(evaluated, Symbol):
        name = evaluated.name
    elif isinstance(evaluated, str):
        name = evaluated

    seval.group = name
    seval.context['CG'] = seval.group

    scope_index = seval.group.rfind('.')
    seval.scope = seval.group[:scope_index + 1] if scope_index != -1 else prev_scope
    seval.context['CS'] = seval.scope

    res = seval.eval(args[1])
    seval.group = prev_group
    seval.scope = prev_scope
    seval.context['CG'] = prev_group
    seval.context['CS'] = prev_scope
    return res


def op_in_groups(seval, args):
    assert len(args) == 2, 'in-groups: exactly two arguments required (in-group group:(symbol+) expression)'
    groups = seval.eval(args[0])
    assert isinstance(groups, list), 'in-groups: first argument must evaluate to list'
    assert groups, 'in-groups: no groups specified'

    res = None
    for group in groups:
        res = op_in_group(seval, [group, args[1]])
    return res


def op_resolve_group(seval, args):
    assert len(args) == 1, 'resolve-group (#): exactly one argument required (resolve-group name:symbol)'
    assert isinstance(args[0], Symbol), 'resolve-group: exactly one argument required (resolve-group name:symbol)'
    if args[0].name in seval.aliases:
        args[0].name = seval.aliases[args[0].name]

    name = seval.context['CG'] + args[0].name

    if seval.traces.contains(name):
        return seval.traces.signal_value(name)


def op_slice(seval, args):
    assert len(args) > 1 and len(args) < 4, 'slice: two or three arguments required (slice high:int [low:int])'
    evaluated = seval.eval_args(args)
    assert isinstance(evaluated[0], (int, list, str)), 'slice: first argument must evaluate to a number or a list'

    if isinstance(evaluated[0], int):
        if len(args) == 2:
            index = evaluated[1]
            assert isinstance(index, int), 'slice: index must evaluate to int'
            return (evaluated[0] & (1 << index)) >> index
        elif len(args) == 3:
            upper = evaluated[1]
            assert isinstance(upper, int), 'slice: upper index must evaluate to int'
            lower = evaluated[2]
            assert isinstance(lower, int), 'slice: lower index must evaluate to int'
            return (evaluated[0] & (((1 << (upper - lower + 1)) - 1) << lower)) >> lower
    elif isinstance(evaluated[0], (list, str)):
        if len(args) == 2:
            index = evaluated[1]
            assert isinstance(index, int), 'slice: index must evaluate to int'
            return evaluated[0][index]
        elif len(args) == 3:
            upper = evaluated[1]
            assert isinstance(upper, int), 'slice: upper index must evaluate to int'
            lower = evaluated[2]
            assert isinstance(lower, int), 'slice: lower index must evaluate to int'
            return evaluated[0][upper:lower]


def op_convert_binary(seval, args):
    assert len(args) == 1 or len(args) == 2, 'convert/bin: expects at least one argument (convert/bin expr:int width:int)'
    evaluated = seval.eval_args(args)
    value = evaluated[0]
    width = evaluated[1] if len(args) == 2 else 0
    assert isinstance(value, int), 'convert/bin: first argument must evaluate to int'
    assert isinstance(width, int), 'convert/bin: second argument must evaluate to int'
    return '{value:0{width}b}'.format(value=value, width=width)


def op_convert_int(seval, args):
    assert len(args) == 1, 'convert/int: expects exactly one argument (convert/int expr:int)'
    return int(seval.eval(args[0]))

        
def op_exit(seval, args):
    assert len(args) < 2, 'exit: expects none or one argument (exit return_code:int)'
    import sys
    if len(args) == 0:
        sys.exit(0)
    else:
        code = seval.eval(args[0])
        assert isinstance(code, int), 'exit: first argument must evaluate to int'
        sys.exit(code)


core_operators = {
    Operator.ATOM.value: op_atom,
    Operator.ADD.value: op_add,
    Operator.SUB.value: op_sub,
    Operator.MUL.value: op_mul,
    Operator.DIV.value: op_div,
    Operator.EXP.value: op_exp,
    Operator.NOT.value: op_not,
    Operator.EQ.value: op_eq,
    Operator.NEQ.value: op_neq,
    Operator.LARGER.value: op_larger,
    Operator.SMALLER.value: op_smaller,
    Operator.LARGER_EQUAL.value: op_larger_equal,
    Operator.SMALLER_EQUAL.value: op_smaller_equal,
    Operator.AND.value: op_and,
    Operator.OR.value: op_or,
    Operator.LET.value: op_let,
    Operator.LETRET.value: op_letret,
    Operator.SET.value: op_set,
    Operator.INC.value: op_inc,
    Operator.PRINT.value: op_print,
    Operator.PRINTF.value: op_printf,
    Operator.IF.value: op_if,
    Operator.COND.value: op_cond,
    Operator.WHEN.value: op_when,
    Operator.UNLESS.value: op_unless,
    Operator.CASE.value: op_case,
    Operator.DO.value: op_do,
    Operator.WHILE.value: op_while,
    Operator.ALIAS.value: op_alias,
    Operator.UNALIAS.value: op_unalias,
    Operator.QUOTE.value: op_quote,
    Operator.EVAL.value: op_eval,
    Operator.DEFUN.value: op_defun,
    Operator.LAMBDA.value: op_lambda,
    Operator.FN.value: op_lambda,
    Operator.GET.value: op_get,
    Operator.IMPORT.value: op_import,
    Operator.CALL.value: op_call,
    Operator.TYPE.value: op_type,
    Operator.REL_EVAL.value: op_rel_eval,
    Operator.SCOPED.value: op_scoped,
    Operator.RESOLVE_SCOPE.value: op_resolve_scope,
    Operator.ALLSCOPES.value: op_allscopes,
    Operator.SETSCOPE.value: op_set_scope,
    Operator.UNSETSCOPE.value: op_unset_scope,
    Operator.GROUPS.value: op_groups,
    Operator.IN_GROUP.value: op_in_group,
    Operator.IN_GROUPS.value: op_in_groups,
    Operator.RESOLVE_GROUP.value: op_resolve_group,
    Operator.SLICE.value: op_slice,
    Operator.EXIT.value: op_exit,
    Operator.CONVERT_BINARY.value: op_convert_binary,
    Operator.CONVERT_INT.value: op_convert_int    
}
