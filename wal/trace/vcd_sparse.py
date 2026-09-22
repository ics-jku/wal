'''Memory-efficient VCD trace implementation using sparse storage.

This parser stores only value changes rather than expanding to a dense
representation. For simulations with many signals that change infrequently,
this can reduce memory usage by orders of magnitude.
'''
import bisect
import re
import sys

from wal.trace.trace import Trace


class TraceVcdSparse(Trace):
    '''Memory-efficient VCD trace using sparse storage.
    
    Instead of storing a value for every signal at every timestamp,
    this implementation stores only the actual value changes and uses
    binary search to find values at any given index.
    '''

    SKIPPED_COMMANDS_HEADER = set(['$comment', '$version', '$date'])

    def __init__(self, filename, tid, container, from_string=False, keep_signals=None):
        super().__init__(tid, filename, container)
        self.timestamps = []
        self.lookup = None
        self.scopes = []
        self.rawsignals = []
        self.all_ids = set()
        self.index2ts = []
        self.name2id = {}
        self.signalinfo = {}
        self.filename = filename
        self.keep_signals = set(keep_signals) if keep_signals else None
        
        # Sparse storage: {signal_name: (change_indices, values)}
        # change_indices[i] is the index at which values[i] becomes active
        self.changes = {}
        
        if from_string:
            self.parse(filename)
        else:
            try:
                with open(filename) as f:
                    self.parse(f.read())
            except FileNotFoundError:
                print(f'Error while loading {filename}. File not found.')
                sys.exit(1)

        self.all_timestamps = self.timestamps.copy()
        self.index = 0
        self.max_index = len(self.index2ts) - 1
        self.signals = set(Trace.SPECIAL_SIGNALS + self.rawsignals)

        self.id2name = {v: k for k, v in self.name2id.items()}
        self.rawsignals_by_handle = [self.id2name[s] for s in self.all_ids if s in self.id2name]
        self.signals_by_handle = set(self.rawsignals_by_handle)

    def parse(self, vcddata):
        '''Parse VCD data into sparse representation.'''
        scope = []
        tokens = vcddata.split()

        i = 0
        header_done = False
        
        # Parse header section (same as TraceVcd)
        while (not header_done) and tokens:
            if tokens[i] == '$scope':
                name = tokens[i + 2]
                name = re.sub(r'\[([0-9]+)\]', r'<\1>', name)
                name = re.sub(r'\(([0-9]+)\)', r'<\1>', name)
                scope.append(name)
                self.scopes.append('.'.join(scope))
                i += 4
            elif tokens[i] == '$var':
                kind = tokens[i + 1]
                width = tokens[i + 2]
                sig_id = tokens[i + 3]
                name = tokens[i + 4]

                name = re.sub(r'\[[0-9]+:[0-9]+\]', '', name)
                name = re.sub(r'\[([0-9]+)\]', r'<\1>', name)
                name = re.sub(r'\(([0-9]+)\)', r'<\1>', name)

                if scope:
                    fullname = '.'.join(scope) + '.' + name
                else:
                    fullname = name
                
                if not self.keep_signals or (fullname in self.keep_signals):
                    self.all_ids.add(sig_id)
                    self.rawsignals.append(fullname)
                    self.name2id[fullname] = sig_id
                    self.signalinfo[sig_id] = {
                        'id': sig_id,
                        'name': fullname,
                        'width': int(width),
                        'kind': kind,
                    }

                if tokens[i + 5] == '$end':
                    i += 6
                elif tokens[i + 5][0] == '[':
                    i += 7
                else:
                    assert False, 'VCD error'
            elif tokens[i] == '$upscope':
                scope.pop()
                i += 2
            elif tokens[i] == '$enddefinitions':
                i += 2
                header_done = True
            elif tokens[i] == '$timescale':
                if tokens[i + 3] == '$end':
                    self.timescale = tokens[i + 1] + tokens[i + 2]
                    i += 4
                elif tokens[i + 2] == '$end':
                    self.timescale = tokens[i + 1]
                    i += 3
            elif tokens[i] in TraceVcdSparse.SKIPPED_COMMANDS_HEADER:
                while tokens[i] != '$end':
                    i += 1
                i += 1
            else:
                i += 1

        # Initialize sparse storage for each signal
        # Format: {signal_id: ([change_indices], [values])}
        sparse_data = {sig_id: ([], []) for sig_id in self.all_ids}
        
        # Track current values for change detection
        current_values = {sig_id: None for sig_id in self.all_ids}
        
        # Parse dump section
        current_index = -1  # Will be 0 after first timestamp
        n_tokens = len(tokens)
        SCALARS = ['x', 'z', 'X', 'Z']

        while i < n_tokens:
            first_char = tokens[i][0]
            
            if first_char == '#':
                # New timestamp
                time = int(tokens[i][1:])
                self.timestamps.append(time)
                self.index2ts.append(time)
                current_index += 1
                i += 1
                
            elif first_char == '0' or first_char == '1':
                # Single-bit value change
                sig_id = tokens[i][1:]
                if sig_id in self.all_ids:
                    new_value = 'b' + first_char
                    if current_values[sig_id] != new_value:
                        current_values[sig_id] = new_value
                        indices, values = sparse_data[sig_id]
                        indices.append(current_index)
                        values.append(new_value)
                i += 1
                
            elif first_char == 'b' or first_char == 'r':
                # N-bit vector: b0000 id
                sig_id = tokens[i + 1]
                if sig_id in self.all_ids:
                    new_value = tokens[i]
                    if current_values[sig_id] != new_value:
                        current_values[sig_id] = new_value
                        indices, values = sparse_data[sig_id]
                        indices.append(current_index)
                        values.append(new_value)
                i += 2
                
            elif first_char in SCALARS:
                # Scalar value change (x, z, X, Z)
                sig_id = tokens[i][1:]
                if sig_id in self.all_ids:
                    new_value = tokens[i][0]
                    if current_values[sig_id] != new_value:
                        current_values[sig_id] = new_value
                        indices, values = sparse_data[sig_id]
                        indices.append(current_index)
                        values.append(new_value)
                i += 1
                
            elif tokens[i] == '$comment':
                while tokens[i] != '$end':
                    i += 1
                i += 1
            else:
                # Skip $dumpvars, $dumpall, $dumpoff, $dumpon, $end
                i += 1

        # Ensure all signals have an initial value at index 0
        for sig_id in self.all_ids:
            indices, values = sparse_data[sig_id]
            if not indices or indices[0] != 0:
                # Insert 'x' at the beginning if no value at index 0
                indices.insert(0, 0)
                values.insert(0, 'x')

        # Convert from id-based to name-based storage
        self.changes = {}
        for signal in self.rawsignals:
            sig_id = self.name2id[signal]
            self.changes[signal] = sparse_data[sig_id]

    def access_signal_data(self, name, index):
        '''Access signal value at given index using binary search.'''
        if self.lookup:
            index = self.lookup[index]
            
        indices, values = self.changes[name]
        
        # Binary search: find rightmost index <= target
        pos = bisect.bisect_right(indices, index) - 1
        
        if pos < 0:
            return 'x'
            
        value = values[pos]
        return self._convert_value(value)
    
    def _convert_value(self, value):
        '''Convert VCD value string to appropriate Python type.'''
        if isinstance(value, str):
            if value.startswith('b'):
                try:
                    return int(value[1:], 2)
                except ValueError:
                    # Contains x or z
                    return value
            elif value.startswith('r'):
                return float(value[1:])
            else:
                # Single char like 'x', 'z', '0', '1'
                return value
        return value

    def set_sampling_points(self, new_indices):
        '''Updates the indices at which data is sampled.'''
        self.lookup = dict(enumerate(new_indices))
        new_timestamps = [self.all_timestamps[i] for i in new_indices]
        self.timestamps = list(dict.fromkeys(new_timestamps))
        self.timestamps = dict(enumerate(self.timestamps))
        self.index = 0
        self.max_index = len(self.timestamps.keys()) - 1

    def signal_width(self, name):
        '''Returns the width of a signal.'''
        return self.signalinfo[self.name2id[name]]['width']
    
    def memory_stats(self):
        '''Return memory usage statistics for debugging.'''
        total_changes = sum(len(indices) for indices, _ in self.changes.values())
        n_signals = len(self.changes)
        n_timestamps = len(self.index2ts)
        dense_size = n_signals * n_timestamps
        
        return {
            'n_signals': n_signals,
            'n_timestamps': n_timestamps,
            'total_changes': total_changes,
            'dense_equivalent': dense_size,
            'compression_ratio': dense_size / total_changes if total_changes > 0 else 0,
        }
