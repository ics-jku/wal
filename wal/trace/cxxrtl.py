'''Trace implementation for the CXXRTL protocoll '''
import asyncio

from wal.trace.trace import Trace

class TraceCxxRtl(Trace):
    '''Holds data for one cxxrtl trace.'''

    def __init__(self, filename, tid, container, from_string=False, keep_signals=None):
        super().__init__(tid, filename, container)
        reader, writer = await asyncio.open_connection(filename, 2205)

    def set_sampling_points(self, new_indices):
        '''Updates the indices at which data is sampled'''
        self.lookup = dict(enumerate(new_indices))
        new_timestamps = [self.all_timestamps[i] for i in new_indices]
        self.timestamps = list(dict.fromkeys(new_timestamps))
        self.timestamps = dict(enumerate(self.timestamps))
        # stores current time stamp
        self.index = 0
        self.max_index = len(self.timestamps.keys()) - 1

    def access_signal_data(self, name, index):
        if self.lookup:
            return self.data[name][self.lookup[index]]
        else:
            return self.data[name][index]
    
    def signal_width(self, name):
        '''Returns the width of a signal'''
        return self.signalinfo[self.name2id[name]]['width']
