'''Implementations for WAL related functions such as loading and unloading traces.'''
import os

from wal.ast_defs import Operator, Symbol, WList
from wal.util import wal_decode
from wal.reader import read_wal_sexprs
from wal.passes import expand, optimize, resolve
from wal.repl import WalRepl


def op_load(seval, args):
    '''Load trace from file filename under id tid '''
    assert len(args) == 1 or len(args) == 2, 'load: expects two arguments (load filename:str|symbol tid:str|symbol?)'
    filename = seval.eval(args[0])
    tid = None
    if len(args) == 2:
      tid = seval.eval(args[1]) if len(args) == 2 else None
      assert isinstance(tid, (str, Symbol)), 'load: second argument must be str or symbol'
      tid = tid.name if isinstance(tid, Symbol) else tid

    assert isinstance(filename, (str, Symbol)), 'load: first argument must be str or symbol'
    filename = filename if isinstance(filename, str) else filename.name
    seval.traces.load(filename, tid)


def op_unload(seval, args):
    '''Removes the trace with id t from WAL '''
    assert len(args) == 1, 'unload: expects one argument (unload trace:symbol)'
    tid = seval.eval(args[0])
    assert isinstance(tid, (str, Symbol)), 'unload: argument must be str or symbol'
    tid = tid if isinstance(tid, str) else tid.name
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


def op_eval_file(seval, args):
    '''Executes WAL module and adds definitions to WAL context'''
    assert len(args) > 0, 'require: expects at least one argument (require module:str|symbol+)'
    assert all(isinstance(s, (str, Symbol)) for s in args), 'require: arguments must be symbols or strings'
    args = [arg.name if isinstance(arg, Symbol) else arg for arg in args]

    for module in args:

        def wal_file_exists(name):
            for path in seval.walpath:
                fname = f'{path}/{name}'
                if os.path.isfile(fname):
                    return fname

            return False

        sexprs = None
        if name := wal_file_exists(module + '.wo'):
            sexprs = wal_decode(name)
        elif name := wal_file_exists(module + '.wal'):
            with open(name, 'r', encoding='utf-8') as file:
                sexprs = read_wal_sexprs(file.read(), name)
        else:
            print(f'require: cant find file {module}.wal')
            raise FileNotFoundError

        if sexprs:
            for sexpr in sexprs:
                expanded = expand(seval, sexpr, parent=seval.global_environment)
                optimized = optimize(expanded)
                resolved = resolve(optimized, start=seval.global_environment.environment)
                seval.eval(resolved)


def op_require(seval, args):
    'Make bindings from a module available in current scope'
    for spec in args:
        if isinstance(spec, Symbol):
            # imports all bindings from the module
            module_name = spec.name
            module = seval.environment.read(module_name)
            for name, binding in module.items():
                assert name in module, f'require: can not require {name} from module {module_name}'
                seval.environment.define(name, binding)
        elif isinstance(spec, (WList, list)):
            if len(spec) > 1 and spec[0] == Symbol('rename-in'):
                # imports only the selected bindings and renames them
                module_name = spec[1].name
                module = seval.environment.read(module_name)
                for rename_binding in spec[2:]:
                    assert isinstance(rename_binding, (WList, list)) \
                        and len(rename_binding) == 2, 'require: rename-in arguments must be tuples'
                    old_name = rename_binding[0].name
                    new_name = rename_binding[1].name
                    assert old_name in module, f'require: can not require {old_name} from module {module_name}'
                    seval.environment.define(new_name, module[old_name])
            elif len(spec) == 3 and spec[0] == Symbol('only-in'):
                # imports only the selected bindings and renames them
                module_name = spec[1].name
                module = seval.environment.read(module_name)
                selected = spec[2]
                assert isinstance(selected, (WList, list)), 'require: only-in expects a list of bindings'
                for binding in selected:
                    assert isinstance(binding, Symbol), 'require: only-in bindings must be symbols'
                    name = binding.name
                    assert name in module, f'require: can not require {name} from module {module_name}'
                    seval.environment.define(name, module[name])
            elif len(spec) == 3 and spec[0] == Symbol('prefix-in'):
                # imports all bindings from the module and prefixes them
                prefix = spec[1]
                assert isinstance(prefix, Symbol), 'require: prefix-in prefix must be a symbol'
                module_name = spec[2].name
                module = seval.environment.read(module_name)
                for name, binding in module.items():
                    assert name in module, f'require: can not require {name} from module {module_name}'
                    seval.environment.define(prefix.name + name, binding)


def op_repl(seval, args):
    '''Starts a REPL in the current context'''
    try:
        WalRepl(seval.wal, intro=WalRepl.dyn_intro).cmdloop()
    except KeyboardInterrupt:
        pass


def op_is_signal(seval, args):
    assert len(args) == 1, 'signal?: expects exactly one argument (signal? s:symbol|string)'
    name = seval.eval(args[0])
    assert isinstance(name, (Symbol, str)), 'signal?: expects exactly one argument (signal? s:symbol|string)'
    return seval.traces.contains(name if isinstance(name, str) else name.name)


wal_operators = {
    Operator.LOAD.value: op_load,
    Operator.UNLOAD.value: op_unload,
    Operator.STEP.value: op_step,
    Operator.EVAL_FILE.value: op_eval_file,
    Operator.REQUIRE.value: op_require,
    Operator.REPL.value: op_repl,
    Operator.IS_SIGNAL.value: op_is_signal,
}
