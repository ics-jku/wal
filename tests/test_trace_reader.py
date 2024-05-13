'''Test wal trace readers'''
import unittest

from wal.core import Wal
from wal.ast_defs import WalEvalError

class BasicParserTest(unittest.TestCase):
    '''Test trace readers'''

    def test_sv_arrays(self):
        '''Test SystemVerilog arrays'''
        for trace_format in ['vcd', 'fst']:
            wal = Wal()
            wal.load(f'tests/traces/sv_struct_array.{trace_format}')
            self.assertEqual(wal.eval_str('TOP.tb.data<0>.data.something'), 5)


class ReadUndefinedSignalTest(unittest.TestCase):
    '''Test trace readers'''

    def test_read_undefined_signals(self):
        '''Test SystemVerilog arrays'''
        for trace_format in ['vcd', 'fst']:
            wal = Wal()
            wal.load(f'tests/traces/sv_struct_array.{trace_format}')

            with self.assertRaises(WalEvalError):
                wal.eval_str('TOP.tb.data<0>.wrongname')

            with self.assertRaises(WalEvalError):
                wal.eval_str('(in-scope "TOP.tb.data<0>" ~wrongname)')

            with self.assertRaises(WalEvalError):
                wal.eval_str('(in-group "TOP.tb.data<0>" #.wrongname)')
