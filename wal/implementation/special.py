from wal.ast import Operator

def op_find(seval, args):
    assert len(args) == 1, 'find: expects exactly one argument (find condition)'
    
    prev_indices = seval.traces.indices()
    found = []
    ended = seval.traces.step()
    while ended == []:
        if seval.eval(args[0]):
            indices = seval.traces.indices()
            found.append(indices if len(indices) > 1 else list(indices.values())[0])

        ended = seval.traces.step()
        
    for trace in seval.traces.traces.values():
        trace.index = prev_indices[trace.tid]

    return found


def op_whenever(seval, args):
    assert len(args) == 2, 'whenever: expects exactly two arguments (whenever condition body)'
    
    prev_indices = seval.traces.indices()
    res = None
    ended = seval.traces.step()
    while ended == []:
        if seval.eval(args[0]):
            res = seval.eval(args[1])

        ended = seval.traces.step()
        
    for trace in seval.traces.traces.values():
        trace.index = prev_indices[trace.tid]

    return res


special_operators = {
    Operator.FIND.value: op_find,
    Operator.WHENEVER.value: op_whenever
}
