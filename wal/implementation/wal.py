from wal.ast_defs import Operator, Symbol
from wal.reader import read_wal_sexprs, ParseError

def op_load(seval, args):
    assert len(args) == 2, 'load: expects two arguments (load filename:str tid:str|symbol)'
    filename = seval.eval(args[0])
    assert isinstance(filename, str), 'load: first argument must be str'
    assert isinstance(args[1], (str, Symbol)), 'load: first argument must be str or symbol'
    tid = args[1] if isinstance(args[1], str) else args[1].name
    seval.traces.load(filename, tid)
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
        evaluated = seval.eval(args[0])
        if isinstance(evaluated, int):
            res = seval.traces.step(evaluated)
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


def op_require(seval, args):
    assert len(args) > 0, 'require: expects at least one argument (require module:symbol+)'
    assert all(isinstance(s, Symbol) for s in args), 'require: all argument must be symbols'
    for module in args:
        old_context = seval.context
        seval.context = {}
        with open(module.name + '.wal', 'r', encoding='utf8') as file:
                try:
                    sexprs = read_wal_sexprs(file.read())
                    for sexpr in sexprs:
                        if sexpr:
                            seval.eval(sexpr)
                except ParseError as e:
                    e.show()
                    exit(os.EX_DATAERR)

                    
        old_context.update(seval.context)
        seval.context = old_context


wal_operators = {
    Operator.LOAD.value: op_load,
    Operator.STEP.value: op_step,
    Operator.REQUIRE.value: op_require
}
