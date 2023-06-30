'''Trace implementation for the VCD file format '''

from wal.trace.trace import Trace

class TraceVcd(Trace):
    '''Holds data for one vcd trace.'''

    SKIPPED_COMMANDS_HEADER = set(['$comment', '$version', '$date'])

    def __init__(self, filename, tid, container, from_string=False, keep_signals=None):
        super().__init__(tid, filename, container)
        self.timestamps = []
        self.scopes = []
        self.rawsignals = []
        self.all_ids = set()
        self.index2ts = []
        self.name2id = {}
        self.data = {}
        self.signalinfo = {}
        self.filename = filename
        self.keep_signals = set(keep_signals) if keep_signals else None
        if from_string:
            self.parse(filename)
        else:
            with open(filename) as f:
                self.parse(f.read())

        self.index = 0
        self.max_index = len(self.index2ts) - 1
        self.signals = set(Trace.SPECIAL_SIGNALS + self.rawsignals)

    def parse(self, vcddata):
        scope = []
        tokens = vcddata.split()

        i = 0
        header_done = False
        # header section
        while (not header_done) and tokens:
            if tokens[i] == '$scope':
                scope.append(tokens[i + 2])
                self.scopes.append('.'.join(scope))
                i += 4
            elif tokens[i] == '$var':
                kind = tokens[i + 1]
                width = tokens[i + 2]
                id = tokens[i + 3]
                name = tokens[i + 4]
                fullname = '.'.join(scope) + '.' + name
                
                if not self.keep_signals or (fullname in self.keep_signals):
                    self.all_ids.add(id)
                    self.rawsignals.append(fullname)
                    self.name2id[fullname] = id
                    self.signalinfo[id] = {
                        'id': id,
                        'name': fullname,
                        'width': width,
                        'kind': kind,
                        'data': {}
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
            elif tokens[i] in TraceVcd.SKIPPED_COMMANDS_HEADER:
                while tokens[i] != '$end':
                    i += 1

                i += 1
            else:
                # this should not happen
                i += 1

        # parse dump section
        time = 0
        n_tokens = len(tokens)

        while i < n_tokens:
            if tokens[i][0] == '#':
                time = int(tokens[i][1:])
                i += 1
                # if this is not the first time copy old values
                if len(self.index2ts) > 0:
                    for id in self.all_ids:
                        self.data[id].append(self.data[id][-1])
                else:
                    # fill initially with all Xs
                    self.data = {id: ['x'] for id in self.all_ids}

                self.timestamps.append(time)
                self.index2ts.append(time)
            elif tokens[i][0] == 'b':
                # n-bit vector of format b0000 id
                id = tokens[i + 1]
                if id in self.all_ids:
                    value = tokens[i][1:]
                    self.data[id][-1] = value
                i += 2
            elif tokens[i][0] in ['0', '1', 'x', 'z', 'X', 'Z']:
                # scalar value change
                id = tokens[i][1:]
                if id in self.all_ids:
                    value = tokens[i][0]
                    self.data[id][-1] = value
                i += 1
            elif tokens[i] == '$comment':
                print('comment')
                while tokens[i] != '$end':
                    print(tokens[i])
                    i += 1

                i += 1
            else:
                # token is most likely one of ['$dumpvars', '$dumpall', '$dumpoff', '$dumpon', '$end']
                # we skip these commands and just read the following changes
                i += 1                

        # modify data to be a lookup by signal name, removes the indirection via the id
        data_by_name = {signal: self.data[self.name2id[signal]] for signal in self.rawsignals}
        self.data = data_by_name

    def access_signal_data(self, name, index):
        return self.data[name][index]
    
    def signal_width(self, name):
        '''Returns the width of a signal'''
        return self.signals[name]['width']
