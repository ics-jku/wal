from riscvmodel import code
from riscvmodel.variant import Variant
from riscvmodel.isa import InstructionILType, InstructionSType, InstructionBType, InstructionJType

variant = Variant('RV32IMC')


def test(l):
    return list(set(sorted(l)))


def epex_valid(value):
    try:
        instr = code.decode(value, variant=variant)
        if isinstance(instr, InstructionILType) or isinstance(instr, InstructionSType):
            return False
        return True
    except:
        return False


def block_end(value):
    return isinstance(code.decode(value), (InstructionBType, InstructionJType))


def decode(instr):
    try:
        op = str(code.decode(instr, variant=Variant('RV32IMC')))
    except Exception:
        op = 'Invalid: ' + str(instr)
    return op
