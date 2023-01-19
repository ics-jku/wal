'''Wrapper class for trace data'''

from functools import lru_cache
import pathlib

from wal.trace.trace import Trace
from wal.trace.vcd import TraceVcd
from wal.trace.fst import TraceFst

class TraceContainer:
    '''Can hold multiple traces and dispatches value access to the correct trace.'''

    def __init__(self):
        self.traces = {}
        self.n_traces = 0
        self.index_stack = []


    def load(self, file, tid='DEFAULT', from_string=False):
        '''Load a trace from file and add it under trace id tid.'''
        file_extension = pathlib.Path(file).suffix
        if file_extension == '.vcd':
            self.traces[tid] = TraceVcd(file, tid, from_string=from_string)
        elif file_extension == '.fst':
            self.traces[tid] = TraceFst(file, tid, from_string=from_string)
        else:
            print(f'File extension "{file_extension}" not supported.')

        self.n_traces += 1
        self.contains.cache_clear()


    def unload(self, tid='DEFAULT'):
        '''Remove the trace tid from the set of loaded traces. '''
        if tid in self.traces:
            del self.traces[tid]
            self.n_traces -= 1
            self.contains.cache_clear()


    def signal_value(self, name, offset=0, scope=''):
        '''Get the value of signal name at current index + offset.'''

        if self.n_traces == 1 and Trace.SCOPE_SEPERATOR not in name:
            trace = list(self.traces.values())[0]
            return trace.signal_value(name, offset, scope)

        if Trace.SCOPE_SEPERATOR in name:
            # extract tid of vcd
            seperator = name.index(Trace.SCOPE_SEPERATOR)
            trace_tid = name[:seperator]
            signal_name = name[seperator+1:]
            assert trace_tid in self.traces, f'No trace with tid {trace_tid}'
            return self.traces[trace_tid].signal_value(signal_name, offset, scope)


        raise RuntimeError('No traces loaded')

    def signal_width(self, name):
        '''Get the value of signal name at current index + offset.'''

        if self.n_traces == 1 and Trace.SCOPE_SEPERATOR not in name:
            trace = list(self.traces.values())[0]
            return trace.signal_width(name)

        if Trace.SCOPE_SEPERATOR in name:
            # extract tid of vcd
            seperator = name.index(Trace.SCOPE_SEPERATOR)
            trace_tid = name[:seperator]
            signal_name = name[seperator+1:]
            assert trace_tid in self.traces, f'No trace with tid {trace_tid}'
            return self.traces[trace_tid].signal_width(signal_name)

        raise RuntimeError('No traces loaded')

    @lru_cache(maxsize=128)
    def contains(self, name):
        '''Return true if a signal with name exists in any trace.'''
        if self.n_traces == 1 and Trace.SCOPE_SEPERATOR not in name:
            return name in (list(self.traces.values())[0]).signals

        if Trace.SCOPE_SEPERATOR in name:
            seperator = name.index(Trace.SCOPE_SEPERATOR)
            trace_tid = name[:seperator]
            signal_name = name[seperator+1:]
            assert trace_tid in self.traces, f'No trace with tid {trace_tid}'
            return signal_name in self.traces[trace_tid].signals

        return False


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


    def store_indices(self):
        '''Store the current indices for all waveforms on a stack'''
        self.index_stack.append(self.indices())


    def restore_indices(self):
        '''Restore the indices for all waveforms from the stack'''
        if self.index_stack:
            indices = self.index_stack.pop()
            for tid, index in indices.items():
                self.traces[tid].set(index)
