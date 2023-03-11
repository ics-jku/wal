'''Trace implementation for the VCD file format '''

import bisect
import os
import sys
from pyDigitalWaveTools.vcd.parser import VcdParser, VcdVarScope, VcdVarParsingInfo
from wal.trace.trace import Trace

class TraceVcd(Trace):
    '''Holds data for one vcd trace.'''

    def __init__(self, filename, tid, from_string=False):
        self.tid = tid
        self.timestamps = []
        self.filename = filename
        self.index = 0
        self.scopes = []
        self.rawsignals = []
        self.name_to_id = {}
        self.data = {}
        self.all_timestamps = set()

        if from_string:
            raise ValueError("FST traces do not support the from_string argument")



        if os.path.getsize(self.filename) > 10000000:
            print('''\033[93mYou opened a VCD file of more than 10mb.
Maybe you should convert it to the FST format. Try "vcd2fst" from GTKWave.\033[0m''', file=sys.stderr)

        with open(self.filename, encoding='utf-8') as vcd_file:
            vcd = VcdParser()
            vcd.parse(vcd_file)
            top = vcd.scope

        self.walk(top)

        self.signals = set(Trace.SPECIAL_SIGNALS + self.rawsignals)
        self.all_timestamps = list(self.all_timestamps)
        self.all_timestamps.sort()
        self.all_timestamps = dict(enumerate(self.all_timestamps))
        self.timestamps = self.all_timestamps
        self.max_index = len(self.timestamps.keys()) - 1

    def remove_leading_radix(self, bits):
        '''Removes the leading radix char inserted by pyDigitalWaveTools'''
        return bits if ((bits[0] == '0') or (bits[0] == '1')) else bits[1:]

    def walk(self, data, scope=''):
        '''Walks the parsed vcd data and gathers all required info'''
        if isinstance(data, VcdVarScope):
            name = data.name
            if name == 'root':
                name = ''

            newscope = f'{scope}{name}'
            if newscope:
                self.scopes.append(newscope)
                newscope = newscope + '.'

            for child in data.children.values():
                self.walk(child, newscope)
        elif isinstance(data, VcdVarParsingInfo):
            name = scope + data.name
            self.all_timestamps = self.all_timestamps.union(set(map(lambda x: x[0], data.data)))
            self.rawsignals.append(name)

            dump = dict(data.data if isinstance(data.vcdId, str) else data.vcdId)
            dump = {k: self.remove_leading_radix(v)  for k, v in dump.items()}

            self.data[name] = {
                'data': dump,
                'indices': list(dump.keys()),
                'width': data.width,
                'type': data.sigType
            }


    def access_signal_data(self, name, index):
        '''Backend specific function for accessing signals in the waveform'''
        index = self.all_timestamps[index]
        keys = self.data[name]['indices']

        if index not in keys:
            index_i = bisect.bisect_left(keys, index) - 1
            return self.data[name]['data'][keys[index_i]]

        return self.data[name]['data'][index]


    def signal_width(self, name):
        '''Returns the width of a signal'''
        return self.data[name]['type']['width']
