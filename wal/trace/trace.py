'''Generic trace class '''


class Trace:
    SCOPE_SEPERATOR = ';'
    SPECIAL_SIGNALS = ['SIGNALS', 'INDEX', 'MAX-INDEX', 'TS', 'TRACE-NAME', 'TRACE-FILE', 'SCOPES']
    SPECIAL_SIGNALS_SET = set(SPECIAL_SIGNALS)


    def set(self, index=0):
        '''Set the index of this trace'''
        self.index = index


    def step(self, steps=1):
        '''Add steps to the index of this trace.
        If the resulting index is invalid the tid of this trace is returned.'''
        rel_index = self.index + steps
        if rel_index < 0 or rel_index >= self.max_index:
            return self.tid
        self.index = rel_index
        return None


    def signal_value(self, name, offset, scope=''): # pylint: disable=R0912
        '''Get the value of signal name at current time + offset.'''
        rel_index = self.index + offset

        res = None
        # handle special variables
        if rel_index >= 0 and rel_index < self.max_index:
            if name in Trace.SPECIAL_SIGNALS:
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
                elif name == 'MAX-INDEX':
                    res = self.max_index
                elif name == 'TS':
                    res = self.ts
                elif name == 'TRACE-NAME':
                    res = self.tid
                elif name == 'TRACE-FILE':
                    res = self.filename
                elif name == 'SCOPES':
                    res = list(self.data.scopes.keys())
            else:
                bits = self.access_signal_data(name, rel_index)
                try:
                    res = int(bits, 2) if bits != 'x' else bits
                except ValueError:
                    if bits in ('x', 'z'):
                        res = bits
                    elif bits is None:
                        res = [] #'! Error, no value !'

        else:
            raise ValueError(f'can not access {name} at negative timestamp')

        return res


    @property
    def ts(self):  # pylint: disable=C0103
        '''Converts the index to the current timestamp.'''
        return self.timestamps.val[self.index]
