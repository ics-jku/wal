'''Implementations for WAL related functions such as loading and unloading traces.'''
import os
from wal.ast_defs import Operator, Symbol
from wal.reader import read_wal_sexprs
from wal.repl import WalRepl


def op_load(seval, args):
    '''Load trace from file filename under id tid '''
    assert len(args) == 2, 'load: expects two arguments (load filename:str tid:str|symbol)'
    filename = seval.eval(args[0])
    assert isinstance(filename, str), 'load: first argument must be str'
    assert isinstance(args[1], (str, Symbol)), 'load: first argument must be str or symbol'
    tid = args[1] if isinstance(args[1], str) else args[1].name
    seval.traces.load(filename, tid)


def op_unload(seval, args):
    '''Removes the trace with id t from WAL '''
    assert len(args) == 1, 'unload: expects one argument (unload trace:symbol)'
    assert isinstance(args[0], (str, Symbol)), 'unload: argument must be str or symbol'
    tid = args[0] if isinstance(args[0], str) else args[0].name
    return seval.traces.unload(tid)


def op_step(seval, args):
    '''Steps the trace or all traces by offset'''
    assert seval.traces.traces, 'step: no traces loaded'

    def do_step(tid, steps=1):
        if isinstance(tid, str):
            return seval.traces.step(tid=tid, steps=steps)
        if isinstance(tid, Symbol):
            return seval.traces.step(tid=tid.name, steps=steps)

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

    return res == []


def op_require(seval, args):
    '''Executes WAL module and adds definitions to WAL context'''
    assert len(args) > 0, 'require: expects at least one argument (require module:symbol+)'
    assert all(isinstance(s, Symbol) for s in args), 'require: all argument must be symbols'
    for module in args:
        old_context = seval.context

        seval.context = {'CS': old_context['CS'],
                         'CG': old_context['CG'],
                         'args': old_context['args']}

        fname = f'{module.name}.wal'
        if os.path.isfile(fname):
            pass
        elif os.path.isfile(os.path.expanduser(f'~/.wal/libs/{fname}')):
            fname = os.path.expanduser(f'~/.wal/libs/{fname}')
        else:
            print(f'require: cant find file {module.name}.wal')
            raise FileNotFoundError

        with open(fname, 'r', encoding='utf-8') as file:
            sexprs = read_wal_sexprs(file.read())
            for sexpr in sexprs:
                if sexpr:
                    seval.eval(sexpr)

        old_context.update(seval.context)
        seval.context = old_context



def op_repl(seval, args): # pylint: disable=W0613
    '''Starts a REPL in the current context'''
    try:
        WalRepl(seval, intro=WalRepl.dyn_intro).cmdloop()
    except KeyboardInterrupt:
        pass


wal_operators = {
    Operator.LOAD.value: op_load,
    Operator.UNLOAD.value: op_unload,
    Operator.STEP.value: op_step,
    Operator.REQUIRE.value: op_require,
    Operator.REPL.value: op_repl,
}
