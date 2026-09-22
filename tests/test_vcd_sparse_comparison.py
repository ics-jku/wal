'''Comparison tests between dense and sparse VCD parsers.

These tests generate large synthetic VCD files to verify correctness
and measure memory efficiency of the sparse parser.
'''
import random
import pytest
from io import StringIO

from wal.trace.container import TraceContainer
from wal.trace.vcd import TraceVcd
from wal.trace.vcd_sparse import TraceVcdSparse


def generate_vcd(n_signals, n_timestamps, change_probability=0.1, seed=42):
    """Generate a synthetic VCD string.
    
    Args:
        n_signals: Number of signals to generate
        n_timestamps: Number of timestamps
        change_probability: Probability that a signal changes at each timestamp
        seed: Random seed for reproducibility
    
    Returns:
        VCD content as string
    """
    random.seed(seed)
    
    lines = []
    
    # Header
    lines.append("$timescale 1ns $end")
    lines.append("$scope module top $end")
    
    # Generate signal definitions
    # Mix of 1-bit and multi-bit signals
    signal_ids = []
    signal_widths = []
    for i in range(n_signals):
        sig_id = f"s{i}"
        signal_ids.append(sig_id)
        
        # 70% 1-bit, 20% 8-bit, 10% 32-bit
        r = random.random()
        if r < 0.7:
            width = 1
        elif r < 0.9:
            width = 8
        else:
            width = 32
        signal_widths.append(width)
        
        lines.append(f"$var wire {width} {sig_id} sig{i} $end")
    
    lines.append("$upscope $end")
    lines.append("$enddefinitions $end")
    
    # Initial values at time 0
    lines.append("#0")
    lines.append("$dumpvars")
    
    current_values = []
    for i, (sig_id, width) in enumerate(zip(signal_ids, signal_widths)):
        if width == 1:
            val = random.choice([0, 1])
            current_values.append(val)
            lines.append(f"{val}{sig_id}")
        else:
            val = random.randint(0, (1 << width) - 1)
            current_values.append(val)
            lines.append(f"b{val:0{width}b} {sig_id}")
    
    lines.append("$end")
    
    # Generate timestamps with value changes
    for ts in range(1, n_timestamps):
        changes_at_ts = []
        
        for i, (sig_id, width) in enumerate(zip(signal_ids, signal_widths)):
            if random.random() < change_probability:
                if width == 1:
                    # Toggle
                    new_val = 1 - current_values[i]
                    current_values[i] = new_val
                    changes_at_ts.append(f"{new_val}{sig_id}")
                else:
                    new_val = random.randint(0, (1 << width) - 1)
                    current_values[i] = new_val
                    changes_at_ts.append(f"b{new_val:0{width}b} {sig_id}")
        
        # Only emit timestamp if there are changes
        if changes_at_ts:
            lines.append(f"#{ts * 10}")  # Timestamps at 10ns intervals
            lines.extend(changes_at_ts)
    
    return "\n".join(lines)


class TestVcdComparisonSmall:
    """Small-scale comparison tests for quick validation."""
    
    def test_small_simulation_values_match(self):
        """Test that both parsers return identical values for small simulation."""
        vcd = generate_vcd(n_signals=10, n_timestamps=100, change_probability=0.2)
        
        tc_dense = TraceContainer()
        trace_dense = TraceVcd(vcd, 'dense', tc_dense, from_string=True)
        
        tc_sparse = TraceContainer()
        trace_sparse = TraceVcdSparse(vcd, 'sparse', tc_sparse, from_string=True)
        
        # Compare all signals at all indices
        for signal in trace_dense.rawsignals:
            for idx in range(trace_dense.max_index + 1):
                dense_val = trace_dense.access_signal_data(signal, idx)
                sparse_val = trace_sparse.access_signal_data(signal, idx)
                assert dense_val == sparse_val, \
                    f"Mismatch at {signal}[{idx}]: dense={dense_val}, sparse={sparse_val}"
    
    def test_signals_and_scopes_match(self):
        """Test that signal and scope lists are identical."""
        vcd = generate_vcd(n_signals=20, n_timestamps=50)
        
        tc_dense = TraceContainer()
        trace_dense = TraceVcd(vcd, 'dense', tc_dense, from_string=True)
        
        tc_sparse = TraceContainer()
        trace_sparse = TraceVcdSparse(vcd, 'sparse', tc_sparse, from_string=True)
        
        assert set(trace_dense.rawsignals) == set(trace_sparse.rawsignals)
        assert trace_dense.scopes == trace_sparse.scopes
        assert trace_dense.max_index == trace_sparse.max_index


class TestVcdComparisonMedium:
    """Medium-scale tests with more signals and timestamps."""
    
    def test_medium_simulation_100_signals_1000_timestamps(self):
        """Test 100 signals over 1000 timestamps."""
        vcd = generate_vcd(n_signals=100, n_timestamps=1000, change_probability=0.05)
        
        tc_dense = TraceContainer()
        trace_dense = TraceVcd(vcd, 'dense', tc_dense, from_string=True)
        
        tc_sparse = TraceContainer()
        trace_sparse = TraceVcdSparse(vcd, 'sparse', tc_sparse, from_string=True)
        
        # Sample check at various indices
        test_indices = [0, 1, 10, 100, 500, 999]
        for signal in trace_dense.rawsignals:
            for idx in test_indices:
                if idx <= trace_dense.max_index:
                    dense_val = trace_dense.access_signal_data(signal, idx)
                    sparse_val = trace_sparse.access_signal_data(signal, idx)
                    assert dense_val == sparse_val, \
                        f"Mismatch at {signal}[{idx}]: dense={dense_val}, sparse={sparse_val}"
    
    def test_sparse_compression_ratio(self):
        """Test that sparse parser achieves good compression with low change rate."""
        # Low change probability = high compression
        vcd = generate_vcd(n_signals=100, n_timestamps=1000, change_probability=0.01)
        
        tc_sparse = TraceContainer()
        trace_sparse = TraceVcdSparse(vcd, 'sparse', tc_sparse, from_string=True)
        
        stats = trace_sparse.memory_stats()
        
        # With 1% change rate, we expect significant compression
        assert stats['compression_ratio'] > 5.0, \
            f"Expected compression ratio > 5, got {stats['compression_ratio']:.2f}"
        
        print(f"\nCompression stats (100 signals, 1000 timestamps, 1% change rate):")
        print(f"  Signals: {stats['n_signals']}")
        print(f"  Timestamps: {stats['n_timestamps']}")
        print(f"  Total changes: {stats['total_changes']}")
        print(f"  Dense equivalent: {stats['dense_equivalent']}")
        print(f"  Compression ratio: {stats['compression_ratio']:.2f}x")


class TestVcdComparisonLarge:
    """Large-scale tests for stress testing."""
    
    @pytest.mark.slow
    def test_large_simulation_500_signals_10000_timestamps(self):
        """Test 500 signals over 10000 timestamps (5M dense entries)."""
        vcd = generate_vcd(n_signals=500, n_timestamps=10000, change_probability=0.02)
        
        tc_dense = TraceContainer()
        trace_dense = TraceVcd(vcd, 'dense', tc_dense, from_string=True)
        
        tc_sparse = TraceContainer()
        trace_sparse = TraceVcdSparse(vcd, 'sparse', tc_sparse, from_string=True)
        
        # Verify max_index matches
        assert trace_dense.max_index == trace_sparse.max_index
        
        # Sample random indices and signals for comparison
        random.seed(123)
        test_signals = random.sample(trace_dense.rawsignals, min(50, len(trace_dense.rawsignals)))
        test_indices = random.sample(range(trace_dense.max_index + 1), min(100, trace_dense.max_index + 1))
        
        for signal in test_signals:
            for idx in test_indices:
                dense_val = trace_dense.access_signal_data(signal, idx)
                sparse_val = trace_sparse.access_signal_data(signal, idx)
                assert dense_val == sparse_val, \
                    f"Mismatch at {signal}[{idx}]: dense={dense_val}, sparse={sparse_val}"
        
        # Report compression
        stats = trace_sparse.memory_stats()
        print(f"\nLarge simulation stats (500 signals, 10000 timestamps):")
        print(f"  Total changes: {stats['total_changes']:,}")
        print(f"  Dense equivalent: {stats['dense_equivalent']:,}")
        print(f"  Compression ratio: {stats['compression_ratio']:.2f}x")
    
    @pytest.mark.slow
    def test_very_large_1000_signals_50000_timestamps(self):
        """Test 1000 signals over 50000 timestamps (50M dense entries)."""
        vcd = generate_vcd(n_signals=1000, n_timestamps=50000, change_probability=0.005)
        
        tc_sparse = TraceContainer()
        trace_sparse = TraceVcdSparse(vcd, 'sparse', tc_sparse, from_string=True)
        
        stats = trace_sparse.memory_stats()
        
        print(f"\nVery large simulation stats (1000 signals, 50000 timestamps):")
        print(f"  Total changes: {stats['total_changes']:,}")
        print(f"  Dense equivalent: {stats['dense_equivalent']:,}")
        print(f"  Compression ratio: {stats['compression_ratio']:.2f}x")
        print(f"  Memory savings: {(1 - 1/stats['compression_ratio']) * 100:.1f}%")
        
        # With 0.5% change rate, expect very high compression
        assert stats['compression_ratio'] > 10.0, \
            f"Expected compression ratio > 10, got {stats['compression_ratio']:.2f}"
        
        # Spot check some values
        random.seed(456)
        test_signals = random.sample(trace_sparse.rawsignals, 20)
        test_indices = [0, 100, 1000, 10000, 25000, trace_sparse.max_index]
        
        for signal in test_signals:
            for idx in test_indices:
                if idx <= trace_sparse.max_index:
                    # Just verify we can access without error
                    val = trace_sparse.access_signal_data(signal, idx)
                    assert val is not None


class TestVcdEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_signal_never_changes(self):
        """Test signal that never changes after initial value."""
        vcd = """$timescale 1ns $end
$scope module top $end
$var wire 1 ! clk $end
$var wire 8 @ static_data $end
$upscope $end
$enddefinitions $end
#0
$dumpvars
0!
b10101010 @
$end
#10
1!
#20
0!
#30
1!
#40
0!
#50
1!
"""
        tc_dense = TraceContainer()
        trace_dense = TraceVcd(vcd, 'd', tc_dense, from_string=True)
        
        tc_sparse = TraceContainer()
        trace_sparse = TraceVcdSparse(vcd, 's', tc_sparse, from_string=True)
        
        # static_data should have same value at all timestamps
        for idx in range(trace_dense.max_index + 1):
            dense_val = trace_dense.access_signal_data('top.static_data', idx)
            sparse_val = trace_sparse.access_signal_data('top.static_data', idx)
            assert dense_val == sparse_val == 170  # 0b10101010 = 170
    
    def test_signal_changes_every_timestamp(self):
        """Test signal that changes at every timestamp (worst case for sparse)."""
        vcd = generate_vcd(n_signals=10, n_timestamps=100, change_probability=1.0)
        
        tc_dense = TraceContainer()
        trace_dense = TraceVcd(vcd, 'd', tc_dense, from_string=True)
        
        tc_sparse = TraceContainer()
        trace_sparse = TraceVcdSparse(vcd, 's', tc_sparse, from_string=True)
        
        # Values should still match
        for signal in trace_dense.rawsignals:
            for idx in range(trace_dense.max_index + 1):
                dense_val = trace_dense.access_signal_data(signal, idx)
                sparse_val = trace_sparse.access_signal_data(signal, idx)
                assert dense_val == sparse_val
        
        # Compression should be ~1x (no benefit, but no penalty either)
        stats = trace_sparse.memory_stats()
        assert stats['compression_ratio'] >= 0.9  # Allow small overhead
    
    def test_x_and_z_values(self):
        """Test handling of X and Z values on single-bit signals.
        
        Note: Multi-bit signals with x/z (like bxxxx or bxx10) are a known
        limitation in TraceVcd - it fails to parse them. This test only
        covers single-bit x/z values which work correctly.
        """
        vcd = """$timescale 1ns $end
$scope module top $end
$var wire 1 ! flag $end
$var wire 1 @ enable $end
$upscope $end
$enddefinitions $end
#0
$dumpvars
x!
z@
$end
#10
1!
#20
0!
1@
#30
z!
0@
"""
        tc_dense = TraceContainer()
        trace_dense = TraceVcd(vcd, 'd', tc_dense, from_string=True)
        
        tc_sparse = TraceContainer()
        trace_sparse = TraceVcdSparse(vcd, 's', tc_sparse, from_string=True)
        
        for signal in ['top.flag', 'top.enable']:
            for idx in range(trace_dense.max_index + 1):
                dense_val = trace_dense.access_signal_data(signal, idx)
                sparse_val = trace_sparse.access_signal_data(signal, idx)
                assert dense_val == sparse_val, f"Mismatch at {signal}[{idx}]"
    
    def test_real_valued_signals(self):
        """Test handling of real (floating point) signals."""
        vcd = """$timescale 1ns $end
$scope module top $end
$var real 64 ! temperature $end
$upscope $end
$enddefinitions $end
#0
$dumpvars
r25.5 !
$end
#10
r26.7 !
#20
r25.5 !
#30
r100.0 !
"""
        tc_dense = TraceContainer()
        trace_dense = TraceVcd(vcd, 'd', tc_dense, from_string=True)
        
        tc_sparse = TraceContainer()
        trace_sparse = TraceVcdSparse(vcd, 's', tc_sparse, from_string=True)
        
        for idx in range(trace_dense.max_index + 1):
            dense_val = trace_dense.access_signal_data('top.temperature', idx)
            sparse_val = trace_sparse.access_signal_data('top.temperature', idx)
            assert dense_val == sparse_val, f"Mismatch at idx {idx}: {dense_val} vs {sparse_val}"


class TestVcdComparisonBenchmark:
    """Benchmark tests to measure performance difference."""
    
    @pytest.mark.slow
    def test_access_performance(self):
        """Measure access time for both parsers."""
        import time
        
        vcd = generate_vcd(n_signals=200, n_timestamps=5000, change_probability=0.02)
        
        # Load both
        tc_dense = TraceContainer()
        trace_dense = TraceVcd(vcd, 'd', tc_dense, from_string=True)
        
        tc_sparse = TraceContainer()
        trace_sparse = TraceVcdSparse(vcd, 's', tc_sparse, from_string=True)
        
        n_accesses = 10000
        random.seed(789)
        
        # Generate random access pattern
        signals = trace_dense.rawsignals
        accesses = [(random.choice(signals), random.randint(0, trace_dense.max_index)) 
                    for _ in range(n_accesses)]
        
        # Benchmark dense
        start = time.perf_counter()
        for sig, idx in accesses:
            trace_dense.access_signal_data(sig, idx)
        dense_time = time.perf_counter() - start
        
        # Benchmark sparse
        start = time.perf_counter()
        for sig, idx in accesses:
            trace_sparse.access_signal_data(sig, idx)
        sparse_time = time.perf_counter() - start
        
        print(f"\nAccess performance ({n_accesses:,} random accesses):")
        print(f"  Dense:  {dense_time*1000:.2f} ms ({n_accesses/dense_time:.0f} accesses/sec)")
        print(f"  Sparse: {sparse_time*1000:.2f} ms ({n_accesses/sparse_time:.0f} accesses/sec)")
        print(f"  Ratio:  {sparse_time/dense_time:.2f}x")
        
        stats = trace_sparse.memory_stats()
        print(f"  Memory compression: {stats['compression_ratio']:.2f}x")


if __name__ == '__main__':
    # Run a quick sanity check
    print("Generating test VCD...")
    vcd = generate_vcd(n_signals=100, n_timestamps=1000, change_probability=0.02)
    print(f"VCD size: {len(vcd):,} bytes")
    
    print("\nLoading with dense parser...")
    tc_dense = TraceContainer()
    trace_dense = TraceVcd(vcd, 'd', tc_dense, from_string=True)
    
    print("Loading with sparse parser...")
    tc_sparse = TraceContainer()
    trace_sparse = TraceVcdSparse(vcd, 's', tc_sparse, from_string=True)
    
    print("\nComparing values...")
    mismatches = 0
    for signal in trace_dense.rawsignals[:10]:  # Check first 10 signals
        for idx in range(min(100, trace_dense.max_index + 1)):
            d = trace_dense.access_signal_data(signal, idx)
            s = trace_sparse.access_signal_data(signal, idx)
            if d != s:
                mismatches += 1
                print(f"  MISMATCH: {signal}[{idx}] dense={d} sparse={s}")
    
    if mismatches == 0:
        print("  All values match!")
    
    stats = trace_sparse.memory_stats()
    print(f"\nMemory stats:")
    print(f"  Signals: {stats['n_signals']}")
    print(f"  Timestamps: {stats['n_timestamps']}")
    print(f"  Total changes: {stats['total_changes']:,}")
    print(f"  Dense equivalent: {stats['dense_equivalent']:,}")
    print(f"  Compression ratio: {stats['compression_ratio']:.2f}x")
