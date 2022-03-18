#!/bin/python
'''Implements a basic function profiling from RISC-V processor waveforms'''
# pylint: disable=W0702,R1732
import sys
import os
import subprocess
from wal.core import Wal

def ranges(binary_file):
    '''This functions extracts the functions from elf files using "nm"'''
    res = []

    if 'RISCV_PREFIX' in os.environ:
        proc = subprocess.Popen( [ os.environ['RISCV_PREFIX'] + 'nm' , '-S', binary_file], stdout=subprocess.PIPE )
    else:
        print('Please add the location of you RISC-V toolchain to the "RISCV_PREFIX" variable.')
        print('Now trying to fall back to the regular "nm"..\n')
        try:
            proc = subprocess.Popen( [ 'nm' , '-S', binary_file], stdout=subprocess.PIPE )
        except:
            print('"nm" not found on system')
            sys.exit(1)

    stdout, _ = proc.communicate()
    symbols = stdout.decode('UTF-8')

    print(f'Functions in "{binary_file}"')
    for line in symbols.split('\n'):
        cols = line.split()
        if len(cols) == 4 and cols[2] == 'T':
            f_name = cols[3]
            start = int(cols[0], 16)
            end = start + int(cols[1], 16) - 4
            print(f'{f_name:>20} {start:x}-{end:x}')
            res.append([f_name, start, end, 0])

    print('\n')
    return res


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:')
        print('  profile.py elf vcd')
        sys.exit(1)

    BIN = sys.argv[1]
    VCD = sys.argv[2]

    functions = ranges(BIN)

    wal = Wal()
    wal.load(VCD)
    wal.eval('(require config)') # require config script to get concrete signal names
    wal.eval('''(defun count-function [addr]
                  (for [f funcs]
                    (when (&& (>= addr f[1]) (<= addr f[2]))
                        (seta dist f[0] (+ (geta dist f[0]) 1)))))''')

    # calculate the time spent in each function, does not take subcalls into account
    dist = {}
    wal.eval('(whenever (&& (> INDEX 0) clk fire) (count-function pc))', funcs=functions, dist=dist)
    # get number of executed instructions
    instructions_executed = wal.eval('(length (find (&& (> INDEX 0) clk fire)))')

    # print results
    IN_KNOWN_FUNCTION = 0
    print('Time spent in functions:')
    for name, count in dist.items():
        IN_KNOWN_FUNCTION += count
        print(f'{name:>20}: {count/instructions_executed*100:.2f}% ({count})')

    print(f'{"other":>20}: {(instructions_executed - IN_KNOWN_FUNCTION)/instructions_executed*100:.2f}% ({instructions_executed - IN_KNOWN_FUNCTION})')
