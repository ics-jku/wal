'''Python helper function for decoding RISC-V instructions'''
# pylint: disable=W0703,E0401
from riscvmodel import code
from riscvmodel.variant import Variant

variant = Variant('RV32IMCZicsr')

def decode(instr):
    '''Decodes a RISC-V instruction and returns a string description'''
    try:
        return str(code.decode(instr, variant))
    except Exception:
        return 'Invalid: ' + str(instr)
