'''Tests for the sparse VCD parser.'''
import pytest
from pathlib import Path

from wal.trace.container import TraceContainer
from wal.trace.vcd import TraceVcd
from wal.trace.vcd_sparse import TraceVcdSparse


TRACES_DIR = Path(__file__).parent / 'traces'


class TestVcdSparseBasic:
    '''Basic functionality tests for sparse VCD parser.'''

    def test_load_sparse_vcd(self):
        '''Test that sparse VCD loads without errors.'''
        tc = TraceContainer()
        tc.load(str(TRACES_DIR / 'counter.vcd'), tid='test', sparse=True)
        assert 'test' in tc.traces
        assert isinstance(tc.traces['test'], TraceVcdSparse)

    def test_load_dense_vcd(self):
        '''Test that dense VCD still works.'''
        tc = TraceContainer()
        tc.load(str(TRACES_DIR / 'counter.vcd'), tid='test', sparse=False)
        assert 'test' in tc.traces
        assert isinstance(tc.traces['test'], TraceVcd)

    def test_signals_match(self):
        '''Test that both parsers find the same signals.'''
        tc_dense = TraceContainer()
        tc_dense.load(str(TRACES_DIR / 'counter.vcd'), tid='t', sparse=False)
        
        tc_sparse = TraceContainer()
        tc_sparse.load(str(TRACES_DIR / 'counter.vcd'), tid='t', sparse=True)
        
        assert tc_dense.signals == tc_sparse.signals

    def test_scopes_match(self):
        '''Test that both parsers find the same scopes.'''
        tc_dense = TraceContainer()
        tc_dense.load(str(TRACES_DIR / 'counter.vcd'), tid='t', sparse=False)
        
        tc_sparse = TraceContainer()
        tc_sparse.load(str(TRACES_DIR / 'counter.vcd'), tid='t', sparse=True)
        
        assert tc_dense.scopes == tc_sparse.scopes


class TestVcdSparseValues:
    '''Test that sparse parser returns correct values.'''

    def test_values_match_at_all_indices(self):
        '''Test that both parsers return same values at all indices.'''
        tc_dense = TraceContainer()
        tc_dense.load(str(TRACES_DIR / 'counter.vcd'), tid='t', sparse=False)
        trace_dense = tc_dense.traces['t']
        
        tc_sparse = TraceContainer()
        tc_sparse.load(str(TRACES_DIR / 'counter.vcd'), tid='t', sparse=True)
        trace_sparse = tc_sparse.traces['t']
        
        # Get all signal names (excluding special signals)
        signals = [s for s in trace_dense.rawsignals]
        
        # Compare values at all indices
        for idx in range(trace_dense.max_index + 1):
            for signal in signals:
                dense_val = trace_dense.access_signal_data(signal, idx)
                sparse_val = trace_sparse.access_signal_data(signal, idx)
                assert dense_val == sparse_val, \
                    f"Mismatch at index {idx}, signal {signal}: dense={dense_val}, sparse={sparse_val}"

    def test_signal_width(self):
        '''Test that signal width is correctly reported.'''
        tc_sparse = TraceContainer()
        tc_sparse.load(str(TRACES_DIR / 'counter.vcd'), tid='t', sparse=True)
        trace = tc_sparse.traces['t']
        
        # The counter signal should be 4 bits wide
        assert trace.signal_width('tb.dut.counter') == 4


class TestVcdSparseMemory:
    '''Test memory efficiency of sparse parser.'''

    def test_memory_stats(self):
        '''Test that memory_stats returns reasonable values.'''
        tc = TraceContainer()
        tc.load(str(TRACES_DIR / 'counter.vcd'), tid='t', sparse=True)
        trace = tc.traces['t']
        
        stats = trace.memory_stats()
        
        assert stats['n_signals'] > 0
        assert stats['n_timestamps'] > 0
        assert stats['total_changes'] > 0
        assert stats['dense_equivalent'] >= stats['total_changes']
        assert stats['compression_ratio'] >= 1.0

    def test_sparse_uses_less_entries(self):
        '''Test that sparse storage uses fewer entries than dense.'''
        tc = TraceContainer()
        tc.load(str(TRACES_DIR / 'counter.vcd'), tid='t', sparse=True)
        trace = tc.traces['t']
        
        stats = trace.memory_stats()
        
        # For a typical VCD, sparse should use significantly fewer entries
        # The counter.vcd has signals that don't change at every timestamp
        assert stats['compression_ratio'] > 1.0, \
            f"Expected compression ratio > 1, got {stats['compression_ratio']}"


class TestVcdSparseFromString:
    '''Test loading VCD from string.'''

    def test_from_string(self):
        '''Test loading VCD content from string.'''
        vcd_content = """$timescale 1ns $end
$scope module top $end
$var wire 1 ! clk $end
$var wire 8 @ data [7:0] $end
$upscope $end
$enddefinitions $end
#0
0!
b00000000 @
#10
1!
#20
0!
b00001111 @
#30
1!
#40
0!
"""
        # Use TraceVcdSparse directly since container.load has issues with from_string
        tc = TraceContainer()
        trace = TraceVcdSparse(vcd_content, 't', tc, from_string=True)
        
        assert 'top.clk' in trace.rawsignals
        assert 'top.data' in trace.rawsignals
        
        # Check values
        assert trace.access_signal_data('top.clk', 0) == 0
        assert trace.access_signal_data('top.clk', 1) == 1
        assert trace.access_signal_data('top.data', 0) == 0
        assert trace.access_signal_data('top.data', 2) == 15  # 0b00001111 = 15
