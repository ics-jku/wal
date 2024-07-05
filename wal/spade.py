from spade import Spade
from pathlib import Path
from wal.core import Wal
from wal.util import Colors, wal_str

class WalAnalysisPass:

    __wal_pass__ = True

    def __init__(self, pass_dirs, wavefile):
        self.pass_dirs = pass_dirs
        self.wavefile = wavefile
        self.testname = Path(wavefile).stem
        self.name = 'WAL Pass'
        wal = Wal()
        # add all the required dirs to walpath
        for pass_dir in pass_dirs:
            wal.append_walpath(pass_dir)

        wal.eval_str('(eval-file spade-definitions)')
        wal.eval_str(f'(define TEST "{self.testname}")')
        self.wal = wal
        self.config_file = wavefile.with_suffix('')
        wal.eval_str(f'(eval-file "{self.config_file}")')
        wal.load(str(wavefile))
        self.top = wal.eval_str('top_name')
        self.spade = Spade(self.top, 'build/state.ron')

        # register spade translation functions
        self.wal.register_operator('spade/translate', lambda seval, args: self.translate(seval, args).split('(')[0])
        self.wal.register_operator('spade/translate-full', lambda seval, args: self.translate(seval, args))
        self.wal.register_operator('log', lambda seval, args: self.log(seval, args))
        self.wal.register_operator('log/info', lambda seval, args: self.log(seval, args))
        self.wal.register_operator('log/analysis', lambda seval, args: self.log(seval, args, severity='analysis'))
        self.wal.register_operator('log/warn', lambda seval, args: self.log(seval, args, severity='warn'))
        self.wal.register_operator('log/error', lambda seval, args: self.log(seval, args, severity='error'))

    def run(self):
        pass

    def translate(self, seval, args):
        signal = seval.eval(args[0])
        if signal.startswith(self.top):
            # if the signal is abolute remove the top name
            signal = signal[len(self.top)+1:]

        value = seval.eval(args[1])
        if isinstance(value, int):
            value = f"{value:b}"

        return self.spade.translate_value(signal, value)

    def log(self, seval, args, severity='info'):
        def tostr(x):
            if isinstance(x, str):
                return x

            return wal_str(x)

        txt = ''.join(map(tostr, seval.eval_args(args)))
        if severity == 'info':
            print(f'[{Colors.green("INFO")}] {txt}')
        elif severity == 'analysis':
            print(f'[{Colors.blue("ANALYSIS")}] {txt}')
        elif severity == 'warn':
            print(f'[{Colors.yellow("WARNING")}] {txt}')
        elif severity == 'error':
            print(f'[{Colors.red("ERROR")}] {txt}')
