'''Implementation of basic read-eval-print-loop'''
# pylint: disable=W0703,C0103
import cmd
import readline
import os

from wal.util import wal_str
from wal.reader import read_wal_sexpr, ParseError
from wal.ast_defs import Operator, Symbol, WList
from wal.trace.trace import Trace
from wal.version import __version__

histfile = os.path.expanduser('~/.wal/.wal_history')
histfile_size = 1000

class WalRepl(cmd.Cmd):
    '''WalRepl class implements basic read-eval-print-loop'''


    std_intro = f'''WAL {__version__}
Exit to OS or terminate running evaluations with CTRL-C'''
    dyn_intro = f'''WAL {__version__}
Started interactive WAL REPL.
Exit to calling script or terminate running evaluations with CTRL-C'''

    terminator = ['(', ')']
    complete_list = [op.value for op in Operator]
    file = None

    def __init__(self, wal, intro=std_intro):
        super().__init__()
        self.wal = wal
        self.intro = intro

    @property
    def prompt(self):
        '''Generate prompt symbol'''
        ids = [f'{k}({self.wal.traces.traces[k].index})' for k in self.wal.traces.traces.keys()]
        traces = ', '.join(ids)
        if self.wal.traces.traces:
            traces = traces + ' '
        return f'{traces}>-> '


    def onecmd(self, line):
        try:
            evaluated = self.wal.eval(line)

            if evaluated is not None:
                print(wal_str(evaluated))

            if readline:
                readline.set_history_length(histfile_size)
                readline.write_history_file(histfile)

        except KeyboardInterrupt:
            print('Keyboard Interrupt')
        except Exception as e:
            print(e)
            print(wal_str(line))


    def precmd(self, line):
        try:
            sexpr = read_wal_sexpr(line)
            # intercept defuns to include them in completion
            if isinstance(sexpr, WList):
                if sexpr[0] == Symbol('defun'):
                    self.complete_list.append(sexpr[1].name)

            return sexpr
        except ParseError as e:
            e.show()
        except Exception as e:
            print(e)
        return None

    def complete(self, text, state):
        return self.completenames(text)[state]

    def completenames(self, text, *ignored):
        tmp = self.complete_list + self.wal.traces.signals

        if len(self.wal.traces.traces) == 1:
            tmp += Trace.SPECIAL_SIGNALS

        candidates = [c for c in tmp if c.startswith(text)]
        candidates.append(None)
        return candidates

    def preloop(self):
        if not os.path.exists(histfile):
            os.makedirs(os.path.expanduser('~/.wal'), exist_ok=True)

        if readline and os.path.exists(histfile):
            readline.read_history_file(histfile)
