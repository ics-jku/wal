from riscvmodel import code
from riscvmodel.variant import Variant
from riscvmodel.isa import InstructionILType, InstructionSType, InstructionBType, InstructionJType

variant = Variant('RV32IMCZicsr')

def decode(instr):
    try:
        op = str(code.decode(instr, variant))
    except Exception:
        op = 'Invalid: ' + str(instr)
    return op
