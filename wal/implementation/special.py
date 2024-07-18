'''Implementations for special hardware related functions'''
from wal.ast_defs import Operator, Symbol, WList

def op_find(seval, args):
    '''Find
       Returns a list of all indices at which the condition in argument 1
       is true. Steps each trace individually.
    '''
    assert len(args) == 1, 'find: expects exactly one argument (find condition)'

    found = []
    for trace in seval.traces.traces.values():
        start_index = trace.index # store current index
        ended = False
        while not ended:
            if seval.eval(args[0]):
                found.append(trace.index)
            ended = trace.step()

        trace.index = start_index # reset trace index

    found = list(set(found))
    found.sort()
    return found


def op_find_g(seval, args):
    '''Find Global
       Returns a list of all indices at which the condition in argument 1
       is true. Steps all traces at the same time to allow conditions defined
       over all traces.
    '''
    assert len(args) == 1, 'find: expects exactly one argument (find condition)'

    prev_indices = seval.traces.indices()
    found = []
    ended = []
    while not ended:
        if seval.eval(args[0]):
            indices = seval.traces.indices()
            found.append(indices if len(indices) > 1 else list(indices.values())[0])

        ended = seval.traces.step()

    for trace in seval.traces.traces.values():
        trace.index = prev_indices[trace.tid]

    return found


def op_whenever(seval, args):
    '''Evaluates body at each index at which condition evaluate to true '''
    assert len(args) >= 2, 'whenever: expects exactly two arguments (whenever condition body)'

    prev_indices = seval.traces.indices()

    res = None
    ended = []
    while not ended:
        if seval.eval(args[0]):
            res = seval.eval_args(args[1:])[-1]

        ended = seval.traces.step()

    for trace in seval.traces.traces.values():
        trace.index = prev_indices[trace.tid]

    return res


def op_fold_signal(seval, args):
    '''Performs a fold operation on the values of signal from index INDEX
    until the stop condition evaluates to true. '''
    assert len(args) == 4, 'fold/signal: expects 3 arguments (fold f acc stop signal)'
    func = seval.eval(args[0])
    assert isinstance(func, list) and (func[0] == Operator.FN), 'fold/signal: not a valid function'
    acc = seval.eval(args[1])
    stop = args[2]
    signal = seval.eval(args[3])
    assert isinstance(signal, Symbol), 'fold/signal: last argument must be a signal'
    assert seval.traces.contains(signal.name), f'fold/signal: signal "{signal.name}" not found'

    # store indices at start
    prev_indices = seval.traces.indices()

    stopped = False
    while not seval.eval(stop) and not stopped:
        if isinstance(func, Operator):
            acc = seval.eval(WList([func, WList([Operator.QUOTE, acc]), WList([Operator.QUOTE, seval.eval(signal)])]))
        else:
            assert func[0] == Operator.FN, 'fold/signal: first argument must be a function'
            acc = seval.eval_lambda(func, [[Operator.QUOTE, acc], [Operator.QUOTE, seval.eval(signal)]])

        stopped = seval.traces.step() != []

    # restore indices to start values
    for trace in seval.traces.traces.values():
        trace.index = prev_indices[trace.tid]

    return acc


def op_signal_width(seval, args):
    '''Returns the width of a signal'''
    assert len(args) == 1, 'signal-width: expects exactly one argument (signal-width signal:str?)'
    arg = seval.eval(args[0])
    assert isinstance(arg, (str, Symbol)), 'signal-width: expects exactly one argument (signal-width signal:str?)'
    name = arg if isinstance(arg, str) else arg.name
    assert seval.traces.contains(name), f'signal-width: no signal "{name}"'
    return seval.traces.signal_width(name)


def op_sample_at(seval, args):
    '''Sets the timestamps of trace t to list xs'''
    assert len(args) == 1 or len(args) == 2, 'sample-at: expects one or two arguments (sample-at timestamps:list? trace:symbol?)'
    timestamps = seval.eval(args[0])
    assert isinstance(timestamps, (WList, list)), 'sample-at: first argument must be a list of integers'
    assert all(map(lambda x: isinstance(x, int), timestamps)), 'sample-at: second argument must be a list of integers'

    if len(args) == 2:
        tid = args[1]
        assert isinstance(tid, Symbol), 'sample-at: second argument must be a symbol'
        seval.traces.traces[tid.name].set_sampling_points(timestamps)
    else:
        for trace in seval.traces.traces.values():
            trace.set_sampling_points(timestamps)

def op_trim_trace(seval, args):
    '''Trims the trace to end at some point'''
    assert len(args) == 2, 'trim-trace: expects exactly one argument (trim-trace t:symbol?|str? e:int?)'
    tid = seval.eval(args[0])
    new_max_index = seval.eval(args[1])
    assert isinstance(tid, (str, Symbol)), 'trim-trace: first argument must evaluate to symbol or string'
    assert isinstance(new_max_index, int), 'trim-trace: second argument must evaluate to int'
    tid = tid.name if isinstance(tid, str) else tid.name
    return seval.traces.traces[tid].set_max_index(new_max_index)


special_operators = {
    Operator.FIND.value: op_find,
    Operator.FIND_G.value: op_find_g,
    Operator.WHENEVER.value: op_whenever,
    Operator.FOLD_SIGNAL.value: op_fold_signal,
    Operator.SIGNAL_WIDTH.value: op_signal_width,
    Operator.SAMPLE_AT.value: op_sample_at,
    Operator.TRIM_TRACE.value: op_trim_trace,
}
