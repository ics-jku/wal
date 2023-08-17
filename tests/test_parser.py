'''Test wal parsers'''
# pylint: disable=C0103, W0611, C0116, W0201
import unittest

from lark import Lark

from wal.reader import read, WAL_GRAMMAR, ParseError, read_wal_sexpr, read_wal_sexprs
from wal.ast_defs import Symbol as S, WList
from wal.ast_defs import Operator as Op

test_readers = {}
def read_test(code, start):
    if start not in test_readers:
        test_readers[start] = Lark(WAL_GRAMMAR, start=start, parser='lalr', propagate_positions=True)

    return read(code, test_readers[start])


class BasicParserTest(unittest.TestCase):
    '''Test basic parsers'''

    def test_boolean(self):
        '''Test boolean parser'''
        self.assertEqual(read_wal_sexpr('#t'), 1)
        self.assertEqual(read_wal_sexpr('#f'), 0)

    def test_binary(self):
        '''Test bin int parser'''
        reader = lambda c: read_test(c, 'bin_int')
        self.assertEqual(reader('0b0'), 0)
        self.assertEqual(reader('0b1'), 1)
        self.assertEqual(reader('0b11'), 3)
        self.assertEqual(reader('0b101010110101'), 2741)
        self.assertRaises(ParseError, reader, '4')
        self.assertRaises(ParseError, reader, 'a')
        self.assertRaises(ParseError, reader, 'u')
        self.assertRaises(ParseError, reader, '(')

    def test_decimal_int(self):
        '''Test dec int parser'''
        reader = lambda c: read_test(c, 'int')
        self.assertEqual(reader('4'), 4)
        self.assertEqual(reader('46'), 46)
        self.assertEqual(reader('-4'), -4)
        self.assertEqual(reader('-46'), -46)
        self.assertRaises(ParseError, reader, '4 6')
        self.assertRaises(ParseError, reader, 'a')
        self.assertRaises(ParseError, reader, '- 4')

    def test_hexadecimal_int(self):
        '''Test hex int parser'''
        reader = lambda c: read_test(c, 'hex_int')
        self.assertEqual(reader('0x4'), 4)
        self.assertEqual(reader('0x46'), 70)
        self.assertEqual(reader('0x4ffaf6'), 0x4ffaf6)
        self.assertRaises(ParseError, reader, '4 6')
        self.assertRaises(ParseError, reader, 'a')
        self.assertRaises(ParseError, reader, '0xh')

    def test_float(self):
        '''Test parsing floats'''
        reader_float = lambda c: read_test(c, 'float')
        reader_sexpr = lambda c: read_test(c, 'sexpr')
        pass_cases = [x / 3.2 for x in range(-500, 500, 15)]
        for case in pass_cases:
            self.assertEqual(reader_float(str(case)), case)
            self.assertEqual(reader_sexpr(str(case)), case)

    def test_text(self):
        '''Test text parser'''
        reader = lambda c: read_test(c, 'string')
        self.assertEqual(reader('"foo"'), 'foo')
        self.assertEqual(reader('"1234"'), '1234')
        self.assertEqual(reader('"\'bar\'"'), '\'bar\'')
        self.assertRaises(ParseError, reader, '1234')

    def test_base_symbol(self):
        '''Test symbol parser'''
        reader_base = lambda c: read_test(c, 'base_symbol')
        reader_symbol = lambda c: read_test(c, 'symbol')
        pass_cases = ['valid', '_valid', 'Valid', 'v123lid', 'va$lid', 'state::bla=>x', 'x2']
        for case in pass_cases:
            self.assertEqual(reader_base(case), S(case))
            self.assertEqual(reader_symbol(case), S(case))

        fail_cases = ['1valid', '%valid%', '\t', '1list', '-d21']
        for case in fail_cases:
            self.assertRaises(ParseError, reader_base, case)
            self.assertRaises(ParseError, reader_symbol, case)

    def test_scoped_symbol(self):
        '''Test symbol parser'''
        reader = lambda c: read_test(c, 'scoped_symbol')
        pass_cases = ['~valid', '~_valid', '~Valid', '~v123li/d', '~va$lid']
        for case in pass_cases:
            self.assertEqual(reader(case), WList([Op.RESOLVE_SCOPE, S(case[1:])]))

        fail_cases = ['1valid', ' valid',
                      'valid%', '  ', '\t', '1list', '-d21']
        for case in fail_cases:
            self.assertRaises(ParseError, reader, case)

    def test_grouped_symbol(self):
        '''Test symbol parser'''
        reader = lambda c: read_test(c, 'grouped_symbol')
        pass_cases = ['#valid', '#_valid', '#Valid', '#v123li/d', '#va$lid']
        for case in pass_cases:
            self.assertEqual(reader(case), WList([Op.RESOLVE_GROUP, S(case[1:])]))

        fail_cases = ['1valid', ' valid',
                      'valid%', '  ', '\t', '1list', '-d21']
        for case in fail_cases:
            self.assertRaises(ParseError, reader, case)

    def test_operators(self):
        '''Test built-in operators'''
        reader = lambda c: read_test(c, 'atom')
        for builtin in Op:
            self.assertEqual(reader(builtin.value),
                             Op(builtin.value))


class SexprParserTest(unittest.TestCase):
    '''Test all parsers related to s-expressions'''

    def test_sexpr(self):
        '''Test simple s-expressions'''
        reader = lambda c: read_test(c, 'sexpr')
        self.assertEqual(reader('5'), 5)
        self.assertEqual(reader('"foo"'), 'foo')
        self.assertEqual(reader('valid'), S('valid'))

        self.assertEqual(reader('(+ 1 2)'), [Op.ADD, 1, 2])
        # self.assertEqual(reader('(+ 1 (- 3 4))'),
        #                  [Op.ADD, 1, [Op.SUB, 3, 4]])

    def test_quoting(self):
        '''Test qouted sexprs'''
        reader = lambda c: read_test(c, 'sexpr')
        self.assertEqual(reader('\'5'), [Op.QUOTE, 5])
        self.assertEqual(reader('\'valid'),
                         [Op.QUOTE, S('valid')])

    def test_sexpr_whtitespace(self):
        '''Test parsing of simple statements'''
        reader = lambda c: read_test(c, 'sexpr')
        golden = [Op.ADD, 1, 2]
        self.assertEqual(reader('(+ 1 2)'), golden)
        self.assertEqual(reader(' (+ 1 2)'), golden)
        self.assertEqual(reader('\n (+ 1 2) '), golden)
        self.assertEqual(reader('\n (+ 1 2) \n '), golden)

    def test_sexpr_simple_nested(self):
        reader = lambda c: read_test(c, 'sexpr')
        golden = [Op.SUB, [Op.ADD, 1, 2]]
        self.assertEqual(reader('(- (+ 1 2))'), golden)

    def test_sexpr_quoted(self):
        reader = lambda c: read_test(c, 'sexpr')
        golden = [Op.QUOTE, [Op.ADD, 1, 2]]
        self.assertEqual(reader("'(+ 1 2)"), golden)

    def test_timed_sexpr(self):
        '''Test relative expression evaluation'''
        reader = lambda c: read_test(c, 'sexpr')
        self.assertEqual(reader('valid@5'), [Op.REL_EVAL, S('valid'), 5])
        self.assertEqual(reader('valid@-5'), [Op.REL_EVAL, S('valid'), -5])
        self.assertEqual(reader('valid@(+ 1 2)'), [Op.REL_EVAL, S('valid'), [Op.ADD, 1, 2]])
        # self.assertEqual(reader('(+ valid 2)@5'), [Op.REL_EVAL, [Op.ADD, S('valid'), 2], 5])
        # self.assertEqual(reader('(+ valid 2)@x'), [Op.REL_EVAL, [Op.ADD, S('valid'), 2], S('x')])
        # self.assertEqual(reader('(+ valid 2)@(* x 2)'), [Op.REL_EVAL, [Op.ADD, S('valid'), 2], [Op.MUL, S('x'), 2]])
        self.assertRaises(ParseError, reader, 'valid @5')
        self.assertRaises(ParseError, reader, 'valid@ 5')

        # self.assertEqual(reader('(+ x y)@-1'), [Op.REL_EVAL, [Op.ADD, S('x'), S('y')], -1])


class SimpleProgramTest(unittest.TestCase):
    '''Test parse simple programs'''

    def test_programs(self):
        '''Test a simple program with two statements'''
        # p = ''''''
        # golden = []
        # self.assertEqual(read_wal_sexprs(p), golden)

        # p = '''

        # '''
        # golden = []
        # self.assertEqual(read_wal_sexprs(p), golden)

        p = '''(+ 1 2)'''
        golden = [[Op.ADD, 1, 2]]
        self.assertEqual(read_wal_sexprs(p), golden)

        p = '''( +   1 (- x 5))'''
        golden = [[Op.ADD, 1, [Op.SUB, S('x'), 5]]]
        self.assertEqual(read_wal_sexprs(p), golden)

        p = '''(+ 1 (- x 5)) x'''
        golden = [[Op.ADD, 1, [Op.SUB, S('x'), 5]], S('x')]
        #a = read_wal_sexprs(p)
        #print(a.pretty())
        self.assertEqual(read_wal_sexprs(p), golden)


        p = '''
        (set [x 5])

        (print (+ 1 (- x 5)))'''
        golden = [[Op.SET, [S('x'), 5]], [Op.PRINT, [Op.ADD, 1, [Op.SUB, S('x'), 5]]]]
        self.assertEqual(read_wal_sexprs(p), golden)

        p = '''
        (set [x 5]) ;comment
        ; comment
           ;comment
        (print (+ 1 (- x 5)))'''
        self.assertEqual(read_wal_sexprs(p), golden)

        p = ''';(+ 1 2)'''
        golden = []
        self.assertEqual(read_wal_sexprs(p), golden)


class SimpleProgramFileTest(unittest.TestCase):
    '''Test parse simple programs from files'''

    def test_program1(self):
        '''Test a simple program with two statements'''
        with open('tests/files/p1.wal', encoding='utf-8') as f:
            p = f.read()
            golden = [[Op.PRINT, 'hello, test'], [Op.ADD, S('x'), 2]]
            self.assertEqual(read_wal_sexprs(p), golden)

    def test_program2(self):
        '''Test a simple program with a when condition'''
        with open('tests/files/p2.wal', encoding='utf-8') as f:
            p = f.read()
            golden = [[S('when'), [Op.AND, S('i_valid'), S('i_ready')], [Op.PRINT, S('i_data')]]]
            self.assertEqual(read_wal_sexprs(p), golden)

    def test_program3(self):
        '''Test a simple program with a syntax error'''
        with open('tests/files/p3.wal', encoding='utf-8') as f:
            p = f.read()
            self.assertRaises(ParseError, read_wal_sexprs, p)
