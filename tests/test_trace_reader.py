'''Test wal trace readers'''
import unittest

from wal.core import Wal

class BasicParserTest(unittest.TestCase):
    '''Test trace readers'''

    def test_sv_arrays(self):
        '''Test SystemVerilog arrays'''
        for trace_format in ['vcd', 'fst']:
            wal = Wal()
            wal.load(f'tests/traces/array.{trace_format}')
            self.assertEqual(wal.eval_str('TOP.tb.data<0>'), 2)
            self.assertEqual(wal.eval_str('TOP.tb.data<1>'), 0)
