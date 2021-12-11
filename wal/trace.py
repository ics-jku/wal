'''Wrapper class for trace data'''
# pylint: disable=R0902
import re
from functools import lru_cache
from vcdvcd import VCDVCD, StreamParserCallbacks

class TraceContainer:
    '''Can hold multiple traces and dispatches value access to the correct trace.'''

    def __init__(self):
        self.traces = {}

    def load(self, file, tid='DEFAULT', from_string=False):
        '''Load a trace from file and add it under trace id tid.'''
        self.traces[tid] = Trace(file, tid, from_string=from_string)

    def signal_value(self, name, offset=0, scope=''):
        '''Get the value of signal name at current index + offset.'''
        if len(self.traces) == 0:
            raise RuntimeError('No traces loaded')

        if len(self.traces) > 1 or Trace.SCOPE_SEPERATOR in name:
            # extract tid of vcd
            seperator = name.index(Trace.SCOPE_SEPERATOR)
            trace_tid = name[:seperator]
            signal_name = name[seperator+1:]
            assert trace_tid in self.traces, f'No trace with tid {trace_tid}'
            return self.traces[trace_tid].signal_value(signal_name, offset, scope)

        trace = list(self.traces.values())[0]
        return trace.signal_value(name, offset, scope)

    @lru_cache()
    def contains(self, name):
        '''Return true if a signal with name exists in any trace.'''
        if len(self.traces) == 0:
            return False

        if len(self.traces) > 1 or Trace.SCOPE_SEPERATOR in name:
            seperator = name.index(Trace.SCOPE_SEPERATOR)
            trace_tid = name[:seperator]
            signal_name = name[seperator+1:]
            assert trace_tid in self.traces, f'No trace with tid {trace_tid}'
            return signal_name in self.traces[trace_tid].signals

        return name in (list(self.traces.values())[0]).signals

    def step(self, steps=1, tid=None):
        '''Step one or all traces.
        If steps is not defined step trace(s) by +1.
        If no trace id (tid) is defined step all traces.
        '''
        ended = []
        if tid:
            assert tid in self.traces, f'No trace with tid {tid}'
            res =  self.traces[tid].step(steps)
            if res:
                ended.append(res)
        else:
            for trace in self.traces.values():
                res = trace.step(steps)
                if res:
                    ended.append(res)
        return ended

    @property
    @lru_cache()
    def scopes(self):
        '''Returns a list of all scopes.
        If more than one scope trace is loaded, scopes are prepended by the tid of their trace.
        '''
        if len(self.traces) > 1:
            scopes = [(trace.id + trace.SCOPE_SEPERATOR + scope) for trace in self.traces.values() for scope in trace.scopes]
        else:
            scopes = [scope for trace in self.traces.values() for scope in trace.scopes]

        return scopes

    @property
    def signals(self):
        '''Returns a list of all signals.
        If more than one scope trace is loaded, signals are prepended by the tid of their trace
        '''
        signals = []
        for trace in self.traces.values():
            if len(self.traces) == 1:
                tmp = list(map(lambda s: f'{s}', trace.rawsignals))
            else:
                tmp = list(map(lambda s, t=trace: f'{t}{Trace.SCOPE_SEPERATOR}{s}', trace.rawsignals))
            signals = signals + tmp
        return signals

    def indices(self):
        '''returns a dict of all current indices'''
        indices = {}
        for trace in self.traces.values():
            indices[trace.tid] = trace.index

        return indices
        # return list(indices.values())[0] if len(indices) == 1 else indices


class Trace:
    '''Holds data for one trace.'''
    SCOPE_SEPERATOR = ';'

    def __init__(self, file, tid, from_string=False):
        self.tid = tid
        self.timestamps = []

        class TimestampCallback(StreamParserCallbacks):  # pylint: disable=R0903
            '''A simple callback used to construct a list of all timestamps'''
            def time(inner, vcd, time, cur_sig_vals):  # pylint: disable=E0213,C0116,W0613,R0201
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
        self.signals = ['TS', 'TRACE-NAME', 'TRACE-FILE', 'SIGNALS', 'INDEX', 'SCOPES'] + self.rawsignals

        # remove duiplicate timestamps, enumerate all timestamps and create look up table
        self.timestamps = list(dict.fromkeys(self.timestamps))
        self.timestamps = dict(enumerate(self.timestamps))
        # stores current time stamp
        self.index = 0
        self.max_index = max(self.timestamps.keys())

        # append tid to scopes
        #self.scopes = list(map(lambda s: tid + Trace.SCOPE_SEPERATOR + s, self.data.scopes))
        self.scopes = self.data.scopes

    def set(self, index=0):
        '''Set the index of this trace'''
        self.index = index

    def step(self, steps=1):
        '''Add steps to the index of this trace.
        If the resulting index is invalid the tid of this trace is returned.'''
        if self.index + steps not in self.timestamps:
            return self.tid
        self.index += steps
        return None

    def signal_value(self, name, offset, scope=''):
        '''Get the value of signal name at current time + offset.'''
        rel_index = self.index + offset

        res = None
        # handle special variables
        if rel_index in self.timestamps:
            if name == 'SIGNALS':
                if scope == '':
                    res = self.rawsignals
                else:
                    def in_scope(signal):
                        prefix_ok = signal.startswith(scope + '.')
                        not_in_sub_scope = '.' not in signal[len(scope) + 1:]
                        return prefix_ok and not_in_sub_scope

                    res = list(filter(in_scope, self.rawsignals))
            elif name == 'INDEX':
                res = self.index
            elif name == 'TS':
                res = self.ts
            elif name == 'TRACE-NAME':
                res = self.tid
            elif name == 'TRACE-FILE':
                res = self.filename
            elif name == 'SCOPES':
                res = list(self.data.scopes.keys())
            else:
                bits = self.data[name][self.timestamps[rel_index]]
                res = int(bits, 2) if bits != 'x' else bits
        else:
            raise ValueError(f'can not access {name} at negative timestamp')

        return res


    @property
    def ts(self):  # pylint: disable=C0103
        '''Converts the index to the current timestamp.'''
        return self.timestamps[self.index]
