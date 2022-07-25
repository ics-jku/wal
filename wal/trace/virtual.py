'''Trace implementation for the FST file format '''

import re
import pylibfst as fst

from wal.trace.trace import Trace

class TraceVirtual(Trace):
    '''Holds data for one fst trace.'''

    def __init__(self, tid, max_index):
        super().__init__(tid, 'virtual')

        self.signals = set()
        self.max_index = max_index
        self.timestamps = range(max_index)
        self.scopes = []


    #def signal_value(self, name, offset, scope=''):
    #    return self.virtual_signals[name].value


    def dump_vcd(self):
        with open(self.tid + '.vcd', 'w') as f:
            f.write('$version\n    WAL\n$end\n')
            f.write('$timescale\n    1ps\n$end\n')
            for signal in self.signals:
                f.write(f'$var reg 32 {signal} {signal} [31:0] $end\n')
            f.write('$enddefinitions $end\n')

            old_index = self.index
            for index in range(int(self.max_index/2)):
                print(index)
                self.index = index
                f.write(f'#{index}\n')
                if index == 0:
                    f.write('$dumpvars\n')
                
                for signal in self.signals:
                    value = self.signal_value(signal, index)
                    width = 32
                    txt = f'{value:0{width}b}'.format(value=value, width=width)
                    f.write(f'b{txt} {signal}\n')
            
            self.index = old_index
        '''
$scope module Top $end
$upscope $end
$enddefinitions $end
#0
$dumpvars
0E
'''
