'''Test wal parsers'''
import unittest

from wal.parsers import *
from wal.ast import S
from wal.ast import Operator as Op

# pylint: disable=C0103
# pylint: disable=W0201


class BasicParserTest(unittest.TestCase):
    '''Test basic parsers'''

    def test_boolean(self):
        '''Test boolean parser'''
        parser = boolean
        self.assertEqual(parser.parse('#t'), 1)
        self.assertEqual(parser.parse('#f'), 0)
        self.assertRaises(ParseError, parser.parse, '523')
        self.assertRaises(ParseError, parser.parse, '"#t"')

    def test_binary(self):
        '''Test bin int parser'''
        parser = binary
        self.assertEqual(parser.parse('b0'), 0)
        self.assertEqual(parser.parse('b1'), 1)
        self.assertEqual(parser.parse('b11'), 3)
        self.assertEqual(parser.parse('b101010110101'), 2741)
        self.assertRaises(ParseError, parser.parse, '4')
        self.assertRaises(ParseError, parser.parse, 'a')
        self.assertRaises(ParseError, parser.parse, 'u')
        self.assertRaises(ParseError, parser.parse, '(')

    def test_decimal_int(self):
        '''Test dec int parser'''
        parser = decimal
        self.assertEqual(parser.parse('4'), 4)
        self.assertEqual(parser.parse('46'), 46)
        self.assertEqual(parser.parse('-4'), -4)
        self.assertEqual(parser.parse('-46'), -46)
        self.assertRaises(ParseError, parser.parse, '4 6')
        self.assertRaises(ParseError, parser.parse, 'a')
        self.assertRaises(ParseError, parser.parse, '- 4')

    def test_hexadecimal_int(self):
        '''Test hex int parser'''
        parser = hexadecimal
        self.assertEqual(parser.parse('0x4'), 4)
        self.assertEqual(parser.parse('0x46'), 70)
        self.assertEqual(parser.parse('0x4ffaf6'), 0x4ffaf6)
        self.assertRaises(ParseError, parser.parse, '4 6')
        self.assertRaises(ParseError, parser.parse, 'a')
        self.assertRaises(ParseError, parser.parse, '0xh')

    def test_text(self):
        '''Test text parser'''
        parser = text
        self.assertEqual(parser.parse('"foo"'), 'foo')
        self.assertEqual(parser.parse('"1234"'), '1234')
        self.assertEqual(parser.parse('"\'bar\'"'), '\'bar\'')
        self.assertRaises(ParseError, parser.parse, '1234')

    def test_symbol(self):
        '''Test symbol parser'''
        parser = symbol
        pass_cases = ['valid', '_valid', 'Valid', 'v123lid', 'va$lid']
        for case in pass_cases:
            self.assertEqual(parser.parse(case), Symbol(case))

        fail_cases = ['1valid', ' valid',
                      'valid%', '  ', '\t', '1list', '-d21']
        for case in fail_cases:
            self.assertRaises(ParseError, parser.parse, case)

    #def test_expr_rel(self):
     #   '''Test relative expression evaluation'''
#        parser = sexpr_rel
#        self.assertEqual(parser.parse('valid@5'), [Op.REL_EVAL, S('valid'), 5])
#        self.assertEqual(parser.parse('valid@-5'), [Op.REL_EVAL, S('valid'), -5])
#        self.assertRaises(ParseError, parser.parse, 'valid @5')
#        self.assertRaises(ParseError, parser.parse, 'valid@ 5')

        #parser = sexpr_rel
        #self.assertEqual(parser.parse('(+ x y)@-1'), [Op.REL_EVAL, [Op.ADD, S('x'), S('y')], -1])
      #  pass

    def test_func(self):
        '''Test built-in func names'''
        parser = func
        for builtin in Op:
            self.assertEqual(parser.parse(builtin.value + ' '),
                             Op(builtin.value))

        self.assertRaises(ParseError, parser.parse, 'srq1')


class SexprParserTest(unittest.TestCase):
    '''Test all parsers related to s-expressions'''

    def test_sexpr(self):
        '''Test simple s-expressions'''
        parser = sexpr
        self.assertEqual(parser.parse('5'), 5)
        self.assertEqual(parser.parse('"foo"'), 'foo')
        self.assertEqual(parser.parse('valid'), S('valid'))

        self.assertEqual(parser.parse('(+ 1 2)'), [Op.ADD, 1, 2])
        self.assertEqual(parser.parse('(+ 1 (- 3 4))'),
                         [Op.ADD, 1, [Op.SUB, 3, 4]])

    def test_quoting(self):
        '''Test qouted sexprs'''
        parser = sexpr
        self.assertEqual(parser.parse('\'5'), [Op.QUOTE, 5])
        self.assertEqual(parser.parse('\'valid'),
                         [Op.QUOTE, S('valid')])

    # def test_statement(self):
    #     '''Test parsing of simple statements'''
    #     parser = statement
    #     golden = Statement([S('valid')], [Op.ADD, 1, 2])
    #     self.assertEqual(parser.parse('valid: (+ 1 2)'), golden)
    #     self.assertEqual(parser.parse('valid  : (+ 1 2)'), golden)
    #     self.assertEqual(parser.parse('valid: \n (+ 1 2)'), golden)

    #     golden = Statement([[Op.NOT, S('valid')]],
    #                        [Op.ADD, 1, 2])
    #     self.assertEqual(parser.parse('(! valid): \n (+ 1 2)'), golden)

    #     # two conditions
    #     golden = Statement([S('valid'), S('ready')],
    #                        [Op.PRINT, 'ok'])
    #     self.assertEqual(parser.parse('valid, ready: (print "ok")'), golden)

    #     # no condition
    #     golden = Statement([True], [Op.PRINT, 'ok'])
    #     self.assertEqual(parser.parse('(print "ok")'), golden)


# class SimpleProgramTest(unittest.TestCase):
#     '''Test parse simple programs'''

#     def test_program1(self):
#         '''Test a simple program with two statements'''
#         parser = program
#         with open('tests/res/p1.wal') as f:
#             p1 = f.read()
#             golden = [Statement([S('BEGIN')], [Op.PRINT, 'Track enable']), Statement(
#                 [S('counter_tb.enable')], [Op.PRINT, 'enable'])]
#             self.assertEqual(parser.parse(p1), golden)

#     def test_program2(self):
#         '''Print payload test'''
#         parser = program
#         with open('tests/res/p2.wal') as f:
#             p2 = f.read()
#             golden = [Statement([S('i_valid'), S('i_ready')], [
#                                 Op.PRINT, S('i_data')])]
#             self.assertEqual(parser.parse(p2), golden)

#     def test_program3(self):
#         '''Print wait cycles test'''
#         parser = program
#         with open('tests/res/p3.wal') as f:
#             p3 = f.read()
#             golden = [Statement([[Op.AND, S('i_valid'),
#                                   [Op.NOT, S('i_ready')]]],
#                                 [Op.LET, S('wait'), [Op.ADD, S('wait'), 1]]),
#                       Statement([S('END')], [Op.PRINT, 'Waited ', S('wait'), ' cycles'])]
#             self.assertEqual(parser.parse(p3), golden)
