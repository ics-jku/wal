'''Trace implementation for the VCD file format '''

import re
from vcdvcd import VCDVCD, StreamParserCallbacks

from wal.trace.trace import Trace

class TraceVcd(Trace):
    '''Holds data for one vcd trace.'''

    def __init__(self, file, tid, from_string=False):
        self.tid = tid
        self.timestamps = []

        class TimestampCallback(StreamParserCallbacks):  # pylint: disable=R0903
            '''A simple callback used to construct a list of all timestamps'''
            def time(inner, vcd, time, cur_sig_vals):  # pylint: disable=E0213,C0116,W0613,W0237
                self.timestamps.append(time)

        if from_string:
            self.data = VCDVCD(vcd_string=file, callbacks=TimestampCallback(), store_scopes=True)
            self.filename = tid
        else:
            self.data = VCDVCD(file, callbacks=TimestampCallback(), store_scopes=True)
            self.filename = file

        # get mapping from name to tid and remove trailing signal wtidth, [31:0] etc.
        self.data.references_to_ids = {re.sub(r'\[\d+:\d+\]', '', k): v for
                                        k, v in self.data.references_to_ids.items()}
        # rename grouped signals like reg(0), reg(1) to reg_0, reg_1
        self.data.references_to_ids = {
            re.sub(r'\(([0-9]+)\)', r'_\1', k): v for k, v in self.data.references_to_ids.items()}

        self.rawsignals = list(self.data.references_to_ids.keys())
        self.signals = set(Trace.SPECIAL_SIGNALS + self.rawsignals)

        # remove duiplicate timestamps, enumerate all timestamps and create look up table
        self.timestamps = list(dict.fromkeys(self.timestamps))
        self.timestamps = dict(enumerate(self.timestamps))
        # stores current time stamp
        self.index = 0
        self.max_index = len(self.timestamps.keys()) - 1

        # append tid to scopes
        #self.scopes = list(map(lambda s: tid + Trace.SCOPE_SEPERATOR + s, self.data.scopes))
        self.scopes = list(self.data.scopes.keys())


    def access_signal_data(self, name, index):
        '''Backend specific function for accessing signals in the waveform'''
        return self.data[name][self.timestamps[index]]


    def signal_width(self, name):
        return int(self.data[name].size)
