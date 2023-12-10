'''Trace implementation for the FST file format '''

from wal.trace.trace import Trace

class TraceVirtual(Trace):
    '''Holds data for one virtual trace.'''

    def __init__(self, tid, max_index, container):
        super().__init__(tid, 'virtual', container)
        self.signals = set()
        self.rawsignals = self.signals
        self.max_index = max_index
        self.timestamps = range(max_index)
        self.scopes = []

    def dump_vcd(self):
        '''Dumps this trace in vcd format'''
         # pylint: disable=C0103
        with open(self.tid + '.vcd', 'w', encoding='utf-8') as f:
            f.write('$version\n    WAL\n$end\n')
            f.write('$timescale\n    1ps\n$end\n')
            f.write(f'$scope module {self.tid} $end\n')
            for signal in self.signals:
                f.write(f'$var reg 32 {signal} {signal} [31:0] $end\n')

            f.write('$upscope $end\n')
            f.write('$enddefinitions $end\n')

            old_index = self.index
            last_values = {}
            for index in range(int(self.max_index/2)):
                self.index = index
                f.write(f'#{index}\n')
                if index == 0:
                    f.write('$dumpvars\n')

                for signal in self.signals:
                    value = self.signal_value(signal, index)
                    if (signal not in last_values) or (value != last_values[signal]):
                        width = 32
                        last_values[signal] = value
                        txt = f'{value:0{width}b}'.format(value=value, width=width)
                        f.write(f'b{txt} {signal}\n')

            self.index = old_index

    def signal_width(self, name):
        return 32

    def get_all_signals(self):
        return list(self.virtual_signals.keys())
