'''Implementations for all basic core functions'''
# pylint: disable=C0116,C0103
import re
import os
import sys
import importlib

from wal.ast_defs import Operator, Symbol, Closure, Environment, Macro, Unquote, UnquoteSplice, WList
from wal.reader import read_wal_sexpr
from wal.passes import expand, optimize, resolve
from wal.util import wal_str


def op_not(seval, args):
    evaluated = seval.eval_args(args)
    assert len(evaluated) >= 1
    assert all(isinstance(arg, int) for arg in evaluated), wal_str(evaluated)
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
    assert all(isinstance(arg, (int, float)) for arg in evaluated)
    return evaluated[0] > evaluated[1]


def op_smaller(seval, args):
    assert len(args) == 2
    evaluated = seval.eval_args(args)
    assert all(isinstance(arg, (int, float)) for arg in evaluated)
    return evaluated[0] < evaluated[1]


def op_larger_equal(seval, args):
    assert len(args) == 2
    evaluated = seval.eval_args(args)
    assert all(isinstance(arg, (int, float)) for arg in evaluated)
    return evaluated[0] >= evaluated[1]


def op_smaller_equal(seval, args):
    assert len(args) == 2
    evaluated = seval.eval_args(args)
    assert all(isinstance(arg, (int, float)) for arg in evaluated)
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
    assert isinstance(args[0], WList), 'let: expects a list of pairs as first argument'
    save_env = seval.environment
    new_env = Environment(parent=save_env)
    seval.environment = new_env

    for pair in args[0]:
        assert isinstance(pair, WList), 'let: expects a list of pairs as first argument'
        assert isinstance(pair[0], Symbol), 'let: first element of let pair must be a Symbol'
        assert len(pair) == 2, 'let: expects a list of pairs as first argument'
        new_env.define(pair[0].name, seval.eval(pair[1]))

    res = seval.eval_args(args[1:])[-1]
    seval.environment = save_env
    return res


def op_set(seval, args):
    assert args, 'set: expects at least one (key:symbol expr) pair'
    for arg in args:
        assert isinstance(arg, WList), 'set: arguments must be (key:symbol expr) tuples'
        assert len(arg) == 2, 'set: arguments must be (key:symbol expr) tuples'
        key = arg[0]
        assert isinstance(key, Symbol), 'set: key must be a symbol'
        res = seval.eval(arg[1])

        # this signal was already resolved
        if key.steps is not None:
            defined_at = seval.environment
            steps = key.steps
            while steps > 0:
                defined_at = seval.environment.parent
                steps -= 1

            # get the dict out of the environment
            defined_at = defined_at.environment
        else:
            defined_at = seval.environment.is_defined(key.name)

        if defined_at:
            defined_at[key.name] = res
        else:
            assert False, f'Write to undefined symbol {key.name}'

    return res


def op_define(seval, args):
    assert len(args) == 2, 'define: expects exactly two arguments (define key:symbol expr)'
    key = args[0]
    assert isinstance(key, Symbol), 'define: key must be a symbol'
    res = seval.eval(args[1])
    seval.environment.define(key.name, res)
    return res


def op_print(seval, args):
    res = [x if isinstance(x, str) else wal_str(x) for x in seval.eval_args(args)]
    print(*res, sep='')


def op_printf(seval, args):
    assert args, 'printf: expects at least a format string'
    format_evaluated = seval.eval(args[0])
    if isinstance(format_evaluated, str):
        def wal_stringify(expr):
            if isinstance(expr, str):
                return expr
            if isinstance(expr, (list, WList, dict, Operator, Unquote, UnquoteSplice, Macro, Closure, Symbol)):
                return wal_str(expr)

            return expr
        
        evaluated = [wal_stringify(e) for e in seval.eval_args(args[1:])]
        try:
            final_str = format_evaluated % tuple(evaluated)
            print(final_str, sep='', end='')
        except Exception as e:
            raise RuntimeError(str(e) + ': "' + format_evaluated + '"') from e
    else:
        raise ValueError('printf\'s first argument must be a format string')


def op_if(seval, args):
    assert len(args) == 2 or len(args) == 3, 'if: expects a condition, if-clause and optionally an else-clause'
    if seval.eval(args[0]):
        return seval.eval(args[1])

    if len(args) == 3:
        return seval.eval(args[2])

    return None


def op_case(seval, args):
    assert args, 'case: expects at least one case argument'
    keyform = seval.eval(args[0])
    clauses = args[1:]
    if len(set(map(lambda x: str(x[0]), clauses))) != len(clauses):
        raise ValueError('case with duplicate key')

    default = None
    for clause in clauses:
        key = clause[0]
        consequents = clause[1:]

        if keyform == key:
            return seval.eval_args(consequents)[-1]

        if isinstance(key, Symbol) and key.name == 'default':
            default = seval.eval_args(consequents)[-1]

    return default


def op_do(seval, args):
    if args:
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

    def chunks(lst, n):
        '''Yield successive n-sized chunks from lst. https://stackoverflow.com/a/312464'''
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    for pair in chunks(args, 2):
        assert isinstance(pair[0], Symbol), 'alias: arguments to alias must be symbols'
        assert isinstance(pair[1], Symbol), 'alias: arguments to alias must be symbols'
        seval.aliases[pair[0].name] = pair[1].name


def op_unalias(seval, args):
    assert len(args) >= 1, 'unalias: expects at least one argument (unalias id:symbol+)'
    for arg in args:
        assert isinstance(arg, Symbol), 'unalias: argument must be a symbol'
        assert arg.name in seval.aliases, f'unalias: no alias {arg.name} known. Can\'t unalias'
        del seval.aliases[arg.name]


def op_quote(seval, args):  # pylint: disable=W0613
    assert len(args) == 1, 'quote: expects exactly one argument'
    return args[0]


def op_quasiquote(seval, args):
    assert len(args) == 1, 'quasiqoute: expects exactly one argument'

    def unquote(expr):
        if isinstance(expr, WList) and len(expr) > 0:
            res = WList([])
            for element in expr:
                if isinstance(element, Unquote):
                    res.append(seval.eval(unquote(element.content)))
                elif isinstance(element, UnquoteSplice):
                    res = res + seval.eval(unquote(element.content))
                else:
                    res.append(unquote(element))

            return res

        return expr

    return unquote(args[0])


def op_unquote(seval, args):
    assert False, 'unquote: not in quasiquote'


def op_eval(seval, args):
    assert len(args) == 1, 'eval: expects exactly one argument'
    evaluated = seval.eval(args[0])
    expanded = expand(seval, evaluated, parent=seval.global_environment)
    optimized = optimize(expanded)
    resolved = resolve(optimized)
    return seval.eval(resolved)


def op_parse(seval, args):
    '''Parses and returns its arguments as WAL expressions'''
    evaluated = seval.eval_args(args)
    assert(all(isinstance(arg, str) for arg in evaluated)), 'parse: all arguments must be string (parse string+)'
    sexprs = [optimize(expand(seval, read_wal_sexpr(arg), parent=seval.global_environment)) for arg in evaluated]
    if len(sexprs) == 1:
        return sexprs[0]

    return WList([Operator.DO] + sexprs)


def op_fn(seval, args):
    assert len(args) >= 2, 'lambda: expects at least two arguments (lambda (symbol | (symbol*)) sexpr)'
    assert isinstance(args[0], (WList, list, Symbol)), 'lambda: first argument must be a list of symbols or a single symbol'
    if isinstance(args[0], (list, WList)):
        assert all(isinstance(arg, Symbol) for arg in args[0]), f'lambda: arguments must be symbols but are {wal_str(args[0])}'

    name = args[1] if isinstance(args[1], (Symbol, str)) else "lambda"

    return Closure(seval.environment, args[0], WList([Operator.DO] + args[1:]), name=name)


def op_defmacro(seval, args):
    assert len(args) >= 3, 'defmacro: expects at least three arguments'
    assert isinstance(args[0], Symbol), f'defmacro: first argument must be a symbol not {args[0]}'
    assert isinstance(args[2], (Symbol, int, str, WList, float)), 'defmacro: third argument must be a valid expression'

    if isinstance(args[0], WList):
        assert all(isinstance(arg, Symbol) for arg in args[0])

    body = WList(list(map(lambda arg: expand(seval, arg), args[2:])))
    seval.environment.define(args[0].name, Macro(args[0].name, args[1], WList([Operator.DO, *body])))


def op_macroexpand(seval, args):
    assert len(args) == 1, 'macroexpand: expects exactly one argument'
    expanded = expand(seval, seval.eval(args[0]), parent=seval.environment)
    optimized = optimize(expanded)
    return optimized


def op_gensym(seval, args):
    seval.gensymi += 1
    return Symbol(f'${seval.gensymi}', 0)


def op_get(seval, args):
    '''get returns the value of a wavefile signal by its string name'''
    assert len(args) == 1, 'get: expects exactly one argument'
    evaluated = seval.eval_args(args)
    if isinstance(evaluated[0], str):
        return seval.eval(Symbol(evaluated[0]))

    if isinstance(evaluated[0], Symbol):
        return seval.eval(evaluated[0])

    return None


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
    split = extern_name.name.split('.')
    func = seval.imports[split[0]]

    for fid in split[1:]:
        func = getattr(func, fid)

    evaluated = list(map(seval.eval, extern_args))
    return func(*evaluated)


def op_type(seval, args):
    '''Return the type of argument'''
    return type(seval.eval(args[0]))


def op_rel_eval(seval, args):
    '''Evaluate an expression at a locally modified index. Index is restored after eval is done.'''
    assert len(args) == 2, 'reval: expects two arguments (reval expr:expr offset:expr->int)'
    assert isinstance(args[0], (Symbol, int, str, WList, list, float)), 'reval: first argument must be a valid expression'
    offset = seval.eval(args[1])
    assert isinstance(offset, int), 'reval: second argument must evaluate to int'
    # check if any trace becomes oob with offset
    for trace in seval.traces.traces.values():
        if trace.index + offset > trace.max_index or trace.index + offset < 0:
            return False

    seval.traces.store_indices()
    seval.traces.step(offset)
    res = seval.eval(args[0])
    seval.traces.restore_indices()
    return res


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
    seval.global_environment.write('CS', seval.scope)
    res = seval.eval(args[1])
    seval.scope = prev_scope
    seval.global_environment.write('CS', prev_scope)
    return res


def op_allscopes(seval, args):
    assert args, 'all-scopes: exactly one argument required'
    assert isinstance(args[0], WList), 'all-scopes: argument must be a valid expression'
    res = []
    prev_scope = seval.global_environment.read('CS')
    for scope in seval.traces.scopes: # pylint: disable=E1101
        seval.scope = scope
        seval.global_environment.write('CS', scope)
        res.append(seval.eval(args[0]))

    seval.global_environment.write('CS', prev_scope)
    return res


def op_resolve_scope(seval, args):
    assert len(args) == 1, 'resolve-scope: exactly one argument required (resolve-scope name:symbol)'
    assert isinstance(args[0], Symbol), 'resolve-scope: exactly one argument required (resolve-scope name:symbol)'
    if args[0].name in seval.aliases:
        args[0].name = seval.aliases[args[0].name]

    if seval.global_environment.read('CS') in seval.traces.scopes:
        # if the scope is a real scope add .
        name = seval.global_environment.read('CS') + '.' + args[0].name
    else:  # if scope is not a real scope it must be a group name, no dot required
        name = seval.global_environment.read('CS') + args[0].name

    assert seval.traces.contains(name), f'resolve-scope: No signal with name "{name}"'
    return seval.traces.signal_value(name)


def op_set_scope(seval, args):
    assert args, 'set-scope: exactly one argument required'
    assert isinstance(args[0], Symbol), f'set-scope: argument must be Symbol but is {type(args[0]).__name__}'
    assert args[0].name in seval.traces.scopes, f'set-scope: {args[0].name} is not a valid scope' # pylint: disable=E1101
    seval.scope = args[0].name
    seval.global_environment.write('CS', args[0].name)


def op_unset_scope(seval, args):
    assert not args, 'unset-scope: expects no arguments'
    seval.scope = ''
    seval.global_environment.write('CS', '')



def op_groups(seval, args):
    '''
    (group "*_ready" "*_valid" "*_data") => all signals (as scope?) for which p_ready, p_valid. exist
    '''
    assert args, 'groups: expects at least one argument (groups post:str+)'

    def process_arg(arg):
        '''evaluates arg if it is a list, else unpacks a signal or just returns a string'''
        if isinstance(arg, WList):
            return seval.eval(arg)
        if isinstance(arg, Symbol):
            return arg.name
        if isinstance(arg, str):
            return arg

        raise RuntimeError('groups: arguments must be string, symbol, or must evaluate to these types')

    def lookup_alias(arg):
        if arg in seval.aliases:
            return seval.aliases[arg]

        return arg

    args = list(map(lookup_alias, map(process_arg, args)))

    if seval.global_environment.read('CS'):
        pattern = re.compile(rf'{seval.global_environment.read("CS")}\.[^\\.]+{args[0]}')
    else:
        pattern = re.compile(rf'.*{args[0]}')

    candidates = list(filter(pattern.fullmatch, seval.traces.signals))
    groups = set()
    for pre in candidates:
        pre = pre[:-len(args[0])]  # cut off filter suffix
        if all(seval.traces.contains(f'{pre}{post}') for post in args[1:]):
            groups.add(pre)

    groups = list(groups)
    groups.sort()

    return groups


def op_in_group(seval, args):
    assert len(args) >= 2, 'in-group: exactly two arguments required (in-group group:symbol expression)'
    prev_group = seval.group
    prev_scope = seval.scope

    evaluated = seval.eval(args[0])
    assert isinstance(evaluated, (str, Symbol)), 'in-group: argument must be Symbol, string or must evaluate to one of them'

    if isinstance(evaluated, Symbol):
        name = evaluated.name
    elif isinstance(evaluated, str):
        name = evaluated

    seval.group = name
    seval.global_environment.write('CG', seval.group)

    scope_index = seval.group.rfind('.')
    seval.scope = seval.group[:scope_index + 1] if scope_index != -1 else prev_scope
    seval.global_environment.write('CS', seval.scope)

    res = seval.eval_args(args[1:])
    seval.group = prev_group
    seval.scope = prev_scope
    seval.global_environment.write('CG', prev_group)
    seval.global_environment.write('CS', prev_scope)
    return res[-1]


def op_in_groups(seval, args):
    assert len(args) >= 2, 'in-groups: exactly two arguments required (in-group group:(symbol+) expression)'
    groups = seval.eval(args[0])
    assert isinstance(groups, (list, WList)), 'in-groups: first argument must evaluate to list'

    res = None
    for group in groups:
        res = op_in_group(seval, [group, *args[1:]])
    return res


def op_resolve_group(seval, args):
    assert len(args) == 1, 'resolve-group (#): exactly one argument required (resolve-group name:symbol)'
    assert isinstance(args[0], Symbol), 'resolve-group: exactly one argument required (resolve-group name:symbol)'
    if args[0].name in seval.aliases:
        args[0].name = seval.aliases[args[0].name]

    name = seval.group + args[0].name

    assert seval.traces.contains(name), f'resolve-group: No signal with name "{name}"'
    return seval.traces.signal_value(name)


def op_slice(seval, args):
    assert len(args) > 1 and len(args) < 4, 'slice: two or three arguments required (slice high:int [low:int])'
    evaluated = seval.eval_args(args)
    assert isinstance(evaluated[0], (int, WList, list, str)), 'slice: first argument must evaluate to a number or a list'

    if isinstance(evaluated[0], int):
        if len(args) == 2: # pylint: disable=R1705
            index = evaluated[1]
            assert isinstance(index, int), 'slice: index must evaluate to int'
            return (evaluated[0] & (1 << index)) >> index
        elif len(args) == 3:
            upper = evaluated[1]
            assert isinstance(upper, int), 'slice: upper index must evaluate to int'
            lower = evaluated[2]
            assert isinstance(lower, int), 'slice: lower index must evaluate to int'
            return (evaluated[0] & (((1 << (upper - lower + 1)) - 1) << lower)) >> lower
    elif isinstance(evaluated[0], (WList, list, str)):
        if len(args) == 2: # pylint: disable=R1705
            index = evaluated[1]
            assert isinstance(index, int), 'slice: index must evaluate to int'
            return evaluated[0][index]
        elif len(args) == 3:
            upper = evaluated[1]
            assert isinstance(upper, int), 'slice: upper index must evaluate to int'
            lower = evaluated[2]
            assert isinstance(lower, int), 'slice: lower index must evaluate to int'
            return evaluated[0][upper:lower]

    return None


def op_loaded_traces(seval, args):
    assert(len(args) == 0), 'loaded-traces: Expects no arguments (loaded-traces)'
    return list(seval.traces.traces.keys())


def op_exit(seval, args):
    assert len(args) < 2, 'exit: expects none or one argument (exit return_code:int)'
    if len(args) == 0:
        sys.exit(0)
    else:
        code = seval.eval(args[0])
        assert isinstance(code, int), 'exit: first argument must evaluate to int'
        sys.exit(code)


core_operators = {
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
    Operator.DEFINE.value: op_define,
    Operator.SET.value: op_set,
    Operator.PRINT.value: op_print,
    Operator.PRINTF.value: op_printf,
    Operator.IF.value: op_if,
    Operator.CASE.value: op_case,
    Operator.DO.value: op_do,
    Operator.WHILE.value: op_while,
    Operator.ALIAS.value: op_alias,
    Operator.UNALIAS.value: op_unalias,
    Operator.QUOTE.value: op_quote,
    Operator.QUASIQUOTE.value: op_quasiquote,
    Operator.UNQUOTE.value: op_unquote,
    Operator.EVAL.value: op_eval,
    Operator.PARSE.value: op_parse,
    Operator.DEFMACRO.value: op_defmacro,
    Operator.MACROEXPAND.value: op_macroexpand,
    Operator.GENSYM.value: op_gensym,
    Operator.FN.value: op_fn,
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
    Operator.LOADED_TRACES.value: op_loaded_traces,
    Operator.EXIT.value: op_exit,
}
