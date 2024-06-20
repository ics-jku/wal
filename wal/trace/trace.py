'''Generic trace class '''
# pylint: disable=E1101, W0201

class Trace:
    '''A generic class for representing waveforms'''
    SCOPE_SEPERATOR = '^'
    SPECIAL_SIGNALS = ['SIGNALS', 'LOCAL-SIGNALS', 'INDEX', 'MAX-INDEX', 'TS', 'TRACE-NAME', 'TRACE-FILE', 'SCOPES', 'LOCAL-SCOPES']
    SPECIAL_SIGNALS_SET = set(SPECIAL_SIGNALS)


    def __init__(self, tid, filename, container):
        self.tid = tid
        self.filename = filename
        self.container = container
        self.virtual_signals = {}
        self.index = 0


    def set(self, index=0):
        '''Set the index of this trace'''
        self.index = index


    def step(self, steps=1):
        '''Add steps to the index of this trace.
        If the resulting index is invalid the tid of this trace is returned.'''
        rel_index = self.index + steps

        if rel_index < 0 or rel_index > self.max_index:
            return self.tid

        self.index = rel_index
        return None


    def signal_value(self, name, offset, scope=''): # pylint: disable=R0912
        '''Get the value of signal name at current time + offset.'''
        rel_index = self.index + offset

        res = None
        # handle special variables
        if 0 <= rel_index <= self.max_index:
            if name in Trace.SPECIAL_SIGNALS:
                if name == 'SIGNALS':
                    res = self.get_all_signals()
                    if len(self.container.traces) > 1:
                        res = [f'{self.tid}{Trace.SCOPE_SEPERATOR}{signal}' for signal in res]
                elif name == 'LOCAL-SIGNALS':
                    if scope == '':
                        res = [s for s in self.rawsignals if '.' not in s]
                    else:
                        def in_scope(signal):
                            prefix_ok = signal.startswith(scope + '.')
                            not_in_sub_scope = '.' not in signal[len(scope) + 1:]
                            return prefix_ok and not_in_sub_scope

                        res = list(filter(in_scope, self.signals))
                elif name == 'INDEX':
                    res = self.index
                elif name == 'MAX-INDEX':
                    res = self.max_index
                elif name == 'TS':
                    res = self.ts
                elif name == 'TRACE-NAME':
                    res = self.tid
                elif name == 'TRACE-FILE':
                    res = self.filename
                elif name == 'LOCAL-SCOPES':
                    if scope != '':
                        scope += '.'
                    res = [s for s in self.scopes if (s.startswith(scope)) and ('.' not in s[len(scope) + 1:])]
                elif name == 'SCOPES':
                    res = self.scopes
            elif name in self.virtual_signals:
                res = self.virtual_signals[name].value
            else:
                bits = self.access_signal_data(name, rel_index)
                try:
                    res = int(bits, 2)
                except ValueError:
                    res = bits
        elif rel_index >= self.max_index:
            res = self.access_signal_data(name, self.max_index)
        else:
            raise ValueError(f'can not access {name} at negative timestamp')

        return res

    def signal_width(self, name):
        '''Returns the signal width'''
        raise NotImplementedError

    @property
    def ts(self):
        '''Converts the index to the current timestamp.'''
        return self.timestamps[self.index]

    def set_sampling_points(self, new_indices):
        '''Updates the indices at which data is sampled'''
        new_timestamps = [self.all_timestamps[i] for i in new_indices]
        self.timestamps = list(dict.fromkeys(new_timestamps))
        self.timestamps = dict(enumerate(self.timestamps))
        # stores current time stamp
        self.index = 0
        self.max_index = len(self.timestamps.keys()) - 1

    def add_virtual_signal(self, signal):
        '''Adds a virtual signal to this trace'''
        self.signals.add(signal.name)
        self.virtual_signals[signal.name] = signal

    def get_all_signals(self):
        return list(self.rawsignals) + list(self.virtual_signals.keys())

    def set_max_index(self, new_max_index):
        self.max_index = min(new_max_index, self.max_index)
        return self.max_index
