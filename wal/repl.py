'''Implementation of basic read-eval-print-loop'''
# pylint: disable=W0703,C0103
import cmd
from wal.util import wal_str
from wal.reader import read_wal_sexpr, ParseError
from wal.ast_defs import Operator
from wal.trace.trace import Trace
from wal.version import __version__


class WalRepl(cmd.Cmd):
    '''WalRepl class implements basic read-eval-print-loop'''

    std_intro = f'WAL {__version__}\n'
    dyn_intro = '''Started interactive WAL REPL.
Exit to calling script with CTRL-C
Exit to OS with (exit)'''
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
        traces = ', '.join(self.wal.traces.traces.keys())
        if self.wal.traces.traces:
            traces = traces + ' '
        return f'{traces}>-> '


    def onecmd(self, line):
        try:
            evaluated = self.wal.eval(line)
            if evaluated is not None:
                print(wal_str(evaluated))
        except Exception as e:
            print(e)
            print(wal_str(line))


    def precmd(self, line):
        try:
            sexpr = read_wal_sexpr(line)
            # intercept defuns to include them in completion
            if isinstance(sexpr, list):
                if sexpr[0] == Operator.DEFUN:
                    self.complete_list.append(sexpr[1].name)

            return sexpr
        except ParseError as e:
            e.show()
        except Exception as e:  # pylint: disable=W0703,C0103
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
