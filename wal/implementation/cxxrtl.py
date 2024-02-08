import base64
import socket
import threading
import socketserver
import json
from functools import partial

from wal.ast_defs import Operator, Symbol, WList
from wal.reader import read_wal_sexpr
from wal.passes import expand, optimize, resolve

class CXXRTLRequestHandler(socketserver.BaseRequestHandler):

    def __init__(self, wal, *args, **kwargs):
        self.wal = wal
        super().__init__(*args, **kwargs)

    def send(self, msg):
        data = bytes(json.dumps(msg) + '\x00', "ascii")
        self.request.sendall(data)

    def read_one_message(self):
        raw_data = b''
        acc = b''
        while b'\x00' not in raw_data:
            raw_data = self.request.recv(1024)
            if not raw_data:
                return None

            acc += raw_data

        return json.loads(str(acc, 'ascii')[:-1])

    def handle(self):
        self.request.setblocking(True)
        while True:
            try:
                msg = self.read_one_message()
                if not msg:
                    return 

                msg_type = msg["type"]

                if msg_type == "greeting":
                    self.greeting()
                elif msg_type == "command":
                    command = msg['command']
                    if command == 'query_interval':
                        self.cmd_query_interval(msg)
                    elif command == 'get_simulation_status':
                        self.cmd_get_simulation_status()
                    elif command == 'list_scopes':
                        self.cmd_list_scopes()
                    elif command == 'list_items':
                        self.cmd_list_items(msg['scope'] if 'scope' in msg else None)
                else:
                    self.send({ 
                        "type": "error",
                        "error": "Unsupported message type",
                        "message": json.dumps(list(self.wal.traces.traces.keys())),
                    })
            except Exception as e:
                print(e)
                self.send({
                    "type": "error",
                    "error": "Malformed message",
                    "message": "The format of the received message is not valid JSON."
                })
                raise e

    def to_time_format(self, time):
        time_fs = time / pow(10, -(15 + self.timescale))
        time_s = int(time_fs / pow(10, 15))
        rem_time_fs = int(time_fs % pow(10, 15))
        return f'{time_s}.{rem_time_fs}'
        
    def cmd_query_interval(self, cmd):
        low_split = cmd['interval'][0].split('.')
        high_split = cmd['interval'][1].split('.')
        low_fs = int(low_split[0]) * pow(10, 15) + int(low_split[1])
        high_fs = int(high_split[0]) * pow(10, 15) + int(high_split[1])

        low = low_fs / pow(10, self.timescale + 15)
        high = high_fs / pow(10, self.timescale + 15)
        
        items = cmd['items']
        encoding = cmd['item_values_encoding']
        diagnostics = cmd['diagnostics']
        collapse = cmd['collapse']

        res = {
            "type": "response",
            "command": "query_interval",
            "samples": []
        }

        trace = list(self.wal.traces.traces.values())[0]
        left_index = trace.ts_to_index_left(low)
        right_index = trace.ts_to_index_right(high) - 1
        path = items.replace(' ', '.')

        # TODO: preparse
        w = f"""(fold (fn [acc i] (if (|| (= INDEX 0) (unstable {path})) (append acc (list {path} TS)) acc)@i) (list) (range {left_index} {right_index}))"""

        expanded = expand(self.wal, read_wal_sexpr(w), parent=self.wal.global_environment)
        optimized = optimize(expanded)
        resolved = resolve(optimized, start=self.wal.global_environment.environment)
        values = [[v[0], self.to_time_format(v[1])] for v in self.wal.eval(resolved)]

        for value in values:
            data = base64.b64encode(value[0].to_bytes()).decode()
            res['samples'].append({
                "time": str(value[1]),
                "item_values": data,
                "diagnostics": [],
            })

        self.send(res)

    def cmd_get_simulation_status(self):
        max_ts = self.wal.eval(read_wal_sexpr('TS@MAX-INDEX'))
        timescale = self.wal.eval(Symbol('TIMESCALE'))
        self.timescale = timescale
        max_time = self.to_time_format(max_ts)
        self.send({
            "type": "response",
            "command": "get_simulation_status",
            "status": "finished",
            "latest_time": max_time,
        })

    def cmd_list_scopes(self):
        res = { 
            'type': 'response',
            'command': 'list_scopes',
            'scopes': {}
        }

        all_scopes = self.wal.eval(read_wal_sexpr('SCOPES'))

        for scope in all_scopes:
            path = ' '.join(scope.split('.'))
            res['scopes'][path] = {
                'src': '',
                'attributes': {}
            }

        self.send(res)

    def cmd_list_items(self, scope):
        res = {
            'type': 'response',
            'command': 'list_items',
            'items': {}
        }

        if scope:
            scope = scope.replace(' ', '.')
            signals = self.wal.eval(read_wal_sexpr(f'(in-scope \'{scope} LOCAL-SIGNALS)'))
        else:
            signals = self.wal.eval(Symbol('SIGNALS'))
                
        for signal in signals:
            path = ' '.join(signal.split('.'))
            res['items'][path] = {
                "src": "",
                "type": "node",
                "width": self.wal.eval(read_wal_sexpr(f'(signal-width \'{signal})')),
                "lsb_at": 0,
                "settable": False,
                "input": False,
                "output": False,
                "attributes": {}
            }

        self.send(res)

    def greeting(self):
        self.send({
            "type": "greeting",
            "version": 0,
            "commands": [
                "list_scopes",
                "list_items",
                "get_simulation_status",
                "query_interval",
            ],
            "events": [],
            "features": {
                "item_values_encoding": ["base64(u32)"]
            }
        })


class CXXRTLServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def op_server_start(seval, args):
    assert len(seval.traces.traces) < 2, 'cxxrtl-server-start: only one loaded trace supported'
    assert not seval.cxxrtl_server, 'cxxrtl-server-start: server is already running'
    assert len(args) >= 1 and len(args) <= 2, 'cxxrtl-server-start: at least one argument required (cxxrtl-server-start port:int? [addr:str?])'
    port = seval.eval(args[0])

    addr = 'localhost'
    if len(args) == 2:
        addr = seval.eval(args[1])
        assert isinstance(addr, str), 'cxxrtl-server-start: addr must evaluate to int (cxxrtl-server-start port:int? [addr:str?])'

    handler = partial(CXXRTLRequestHandler, seval)
    server = CXXRTLServer((addr, port), handler)
    seval.cxxrtl_server = server

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print(f'CXXRTL debug server listening at {addr}:{port}')

def op_server_stop(seval, args):
    assert seval.cxxrtl_server, 'cxxrtl-server-stop: server is not running'
    seval.cxxrtl_server.shutdown()
    seval.cxxrtl_server = None

    print('CXXRTL debug server stopped')

cxxrtl_operators = {
    Operator.CXXRTL_SERVER_START.value: op_server_start,
    Operator.CXXRTL_SERVER_STOP.value: op_server_stop,
}
