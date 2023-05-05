from spade import Spade
from pathlib import Path
from wal.core import Wal

class WalAnalysisPass:

    __wal_pass__ = True
    
    def __init__(self, pass_dir, wavefile):
        self.pass_dir = pass_dir
        self.wavefile = wavefile
        self.testname = Path(wavefile).stem
        self.name = 'WAL Pass'
        wal = Wal()
        wal.append_walpath(pass_dir)
        self.wal = wal
        self.config_file = wavefile.with_suffix('')
        wal.eval_str(f'(require "{self.config_file}")')
        wal.load(wavefile)
        self.top = wal.eval_str('top_name')
        self.spade = Spade(self.top, 'build/state.ron')

        # register spade translation functions
        self.wal.register_operator('spade/translate', lambda seval, args: self.translate(seval, args).split('(')[0])
        self.wal.register_operator('spade/translate-full', lambda seval, args: self.translate(seval, args))

    def run(self):
        pass

    def translate(self, seval, args):
        signal = seval.eval(args[0])[len(self.top)+1:]
        value = seval.eval(args[1])
        if isinstance(value, int):
            value = f"{value:b}"

        return self.spade.translate_value(signal, value)
