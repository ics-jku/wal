from wal.ast_defs import Operator, Symbol

def op_load(seval, args):
    assert len(args) == 2, 'load: expects two arguments (load filename:str tid:str|symbol)'
    assert isinstance(args[0], str), 'load: first argument must be str'
    assert isinstance(args[1], (str, Symbol)), 'load: first argument must be str or symbol'
    tid = args[1] if isinstance(args[1], str) else args[1].name
    seval.traces.load(args[0], tid)
    res = tid

def op_step(seval, args):
    assert seval.traces.traces, 'step: no traces loaded'
    
    def do_step(tid, steps=1):
        if isinstance(tid, str):
            return seval.traces.step(tid=tid, steps=steps)
        elif isinstance(tid, Symbol):
            return seval.traces.step(tid=tid.name, steps=steps)
        else:
            raise ValueError('step: arguments must be either str or symbol')
            
    # step all traces +1
    if len(args) == 0:
        res = seval.traces.step()
    elif len(args) == 1:
        if isinstance(args[0], int):
            res = seval.traces.step(args[0])
        else:
            res = do_step(args[0])
    else:
        evaluated = seval.eval(args[-1])
        assert isinstance(evaluated, int), 'step: last argument must be int'
        steps = evaluated
        res = []
        for tid in args[:-1]:
            step = do_step(tid, steps)
            if step:
                res.append(step)

    return True if res == [] else False

wal_operators = {
    Operator.LOAD.value: op_load,
    Operator.STEP.value: op_step
}
