'''Implementations for type related functions such as type checking'''
from wal.ast_defs import Operator, Symbol, WList
from wal.trace.virtual import TraceVirtual


def op_defsig(seval, args):
    '''Creates a new signal whose value is calculated by evaluating
    the body expressions. '''
    assert len(args) > 1, 'virtual: expects at least two arguments (virtual [name bits] body+)'
    scope_name = seval.global_environment.read('CS')
    scope_sep = '.' if scope_name != '' else ''
    scope = scope_name + scope_sep
    group = seval.global_environment.read('CG') 
    if group != '':
        # groups already include the scope so reset it
        scope = ''

    if isinstance(args[0], (WList, list)):
        assert len(args[0]) == 2, 'defsig: name must either be a name or a (name:symbol width:int) tuple'
        assert isinstance(args[0][0], Symbol), 'defsig: name must either be a name or a (name:symbol width:int) tuple'
        assert isinstance(args[0][1], int), 'defsig: name must either be a name or a (name:symbol width:int) tuple'
        name = f'{scope}{group}{args[0][0].name}'
        width = args[0][1]
    else:
        name = f'{scope}{group}{args[0].name}'
        width = 32

    def resolve(expr):
        if isinstance(expr, WList):
            if len(expr) == 2 and isinstance(expr[1], Symbol):
                if expr[0] == Operator.RESOLVE_SCOPE:
                    return Symbol(f'{scope}{expr[1].name}')
                elif expr[0] == Operator.RESOLVE_GROUP:
                    return Symbol(f'{group}{expr[1].name}')

            return WList(list(map(resolve, expr)))

        return expr

    body = WList(list(map(resolve, args[1:])))
    seval.traces.add_virtual_signal(name, width, body, seval)


def op_new_trace(seval, args):
    '''Create a new virtual trace for id'''
    assert len(args) == 2, 'new-trace: expects one argument (new-trace id:symbol max-index:int)'
    assert isinstance(args[0], Symbol), 'new-trace: first argument must be a symbol'
    assert isinstance(args[1], int), 'new-trace: second argument must be an int'

    seval.traces.traces[args[0].name] = TraceVirtual(args[0].name, args[1], seval.traces)
    seval.traces.n_traces += 1


def op_dump_trace(seval, args):
    '''Dumps the given trace as in vcd format.'''
    seval.traces.traces[args[0].name].dump_vcd()


virtual_operators = {
    Operator.DEFSIG.value: op_defsig,
    Operator.NEWTRACE.value: op_new_trace,
    Operator.DUMPTRACE.value: op_dump_trace,
}
