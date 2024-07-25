'''Trace implementation for the CSV file format, as exported by Logic 2 '''
import re

from wal.trace.trace import Trace

class TraceCsv(Trace):
    '''Holds data for one csv trace.'''

    def __init__(self, filename, tid, container, from_string=False, keep_signals=None):
        super().__init__(tid, filename, container)
        self.timestamps = []
        self.lookup = None # performs index translation after set-sampling
        self.scopes = []
        self.rawsignals = []
        self.index2ts = []
        self.data = {}
        self.signalinfo = {}
        self.filename = filename
        self.keep_signals = set(keep_signals) if keep_signals else None
        if from_string:
            self.parse(filename)
        else:
            with open(filename) as f:
                self.parse(f.read())

        self.all_timestamps = self.timestamps.copy()
        self.index = 0
        self.max_index = len(self.index2ts) - 1
        self.signals = set(Trace.SPECIAL_SIGNALS + self.rawsignals)

    def parse(self, csvdata):
        data = csvdata.strip().split("\n")  # assume row delimiter \n
        header = data[0].split(",") # assume col delimiter ,
        data = [line.split(",") for line in data[1:]]
        time_idx = header.index("Time [s]") # assume timestamp in seconds
        names = [v for v in header if v != "Time [s]"]
        self.data = {}
        
        for name in names:
            kind = "wire"
            width = 1
            orig_name = name
            # replace space with underscore
            name = re.sub(' ', '_', name)
            # remove slice info from names
            name = re.sub(r'\[[0-9]+:[0-9]+\]', '', name)
            # array signals should not clash with WAL operators
            name = re.sub(r'\[([0-9]+)\]', r'<\1>', name)
            name = re.sub(r'\(([0-9]+)\)', r'<\1>', name)
            header[header.index(orig_name)] = name
            self.data[name] = []
            if not self.keep_signals or (name in self.keep_signals):
                self.rawsignals.append(name)
                self.signalinfo[name] = {
                    'name': name,
                    'width': width,
                    'kind': kind,
                    'data': {}
                }
        
        

        pattern = re.compile(r"^(\d+)\.?(\d+)?$")
        for i in range(len(data)):
            # convert timestamp to nanoseconds
            m = pattern.match(data[i][time_idx])
            time_pre, time_post = m.groups("0")
            time_ns = int(f"{time_pre}{time_post.ljust(9, '0')}", base=10)
            
            for x in range(len(data[i])):
                if x != time_idx:
                    self.data[header[x]].append(data[i][x])
            self.timestamps.append(time_ns)
            self.index2ts.append(time_ns)

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
        return self.signalinfo[name]['width']