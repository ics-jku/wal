'''Test wal eval logic'''
import unittest
import random

from wal.core import Wal
from wal.ast_defs import WalEvalError


class BasicOpTest(unittest.TestCase):
    '''Test built-in functions'''

    def setUp(self):
        self.wal = Wal()

    def checkEqual(self, txt, res):
        '''eval first argument and check if result matches second argument '''
        self.assertEqual(self.wal.eval_str(txt), res)

    def test_is_atom(self):
        '''Test atom?'''

        self.checkEqual('(atom? 1)', True)
        self.checkEqual('(atom? "1")', True)
        self.checkEqual("(atom? (+ 1 2))", True)
        self.checkEqual("(atom? '(+ 1 2))", False)
        self.checkEqual("(atom? (array))", False)

    def test_is_symbol(self):
        '''Test symbol?'''

        self.checkEqual("(symbol? 'a)", True)
        self.checkEqual("(symbol? 'TOP.sub.sig)", True)
        self.wal.eval_str("(define x 'a)")
        self.checkEqual("(symbol? x)", True)
        self.checkEqual('(symbol? "symbol")', False)
        self.checkEqual('(symbol? (let ([a 5]) a))', False)
        self.checkEqual('(symbol? 1)', False)
        self.checkEqual("(symbol? '(1 2))", False)
        self.checkEqual("(symbol? (array))", False)

    def test_is_string(self):
        '''Test string?'''

        self.checkEqual('(string? "1")', True)
        self.checkEqual('(string? "1897342hahdasd \\n asa")', True)
        self.checkEqual('(string? (+ "hi" 1))', True)
        self.checkEqual("(string? (symbol->string 'a))", True)

        self.checkEqual('(string? 1)', False)
        self.checkEqual('(let ([a 5]) (string? a))', False)
        self.checkEqual("(string? 'a)", False)
        self.checkEqual("(string? '(1 2))", False)
        self.checkEqual("(string? (array))", False)

    def test_is_int(self):
        '''Test int?'''

        self.checkEqual("(int? 1)", True)
        self.checkEqual("(int? 1142441)", True)
        self.checkEqual("(int? 583547542375894327581)", True)
        self.checkEqual("(int? (+ 1 2))", True)

        self.checkEqual("(int? ''1)", False)
        self.checkEqual("(int? 'a)", False)
        self.checkEqual("(int? '(1 2))", False)
        self.checkEqual('(int? "a")', False)
        self.checkEqual("(int? (array))", False)

    def test_is_list(self):
        '''Test list?'''

        self.checkEqual("(list? '(1 2 3))", True)
        self.checkEqual("(list? (range 10))", True)
        self.checkEqual("(list? '(+ 1 2))", True)

        self.checkEqual("(list? (&& 123))", False)
        self.checkEqual("(list? 'a)", False)
        self.checkEqual('(list? "a")', False)
        self.checkEqual("(list? (array))", False)

    def test_convert_binary(self):
        '''Test convert/bin'''

        self.checkEqual("(convert/bin 0)", "0")
        self.checkEqual("(convert/bin 0 5)", "00000")
        self.checkEqual("(convert/bin 1)", "1")
        self.checkEqual("(convert/bin 1 5)", "00001")
        self.checkEqual("(convert/bin (+ 1 2))", "11")

        for _ in range(50):
            random_int = random.randint(-99999999, 9999999)
            random_width = random.randint(1, 100)
            int_str = self.wal.eval_str(f"(convert/bin {random_int} {random_width})")
            self.assertEqual(random_int, int(int_str, 2))

        with self.assertRaises(WalEvalError):
            self.wal.eval_str('(convert/bin "hi")')

        with self.assertRaises(WalEvalError):
            self.wal.eval_str('(convert/bin (quote a))')

    def test_string_to_int(self):
        '''Test string->int'''

        self.checkEqual('(string->int "0")', 0)
        self.checkEqual('(string->int "1")', 1)
        self.checkEqual('(string->int "00000")', 0)
        self.checkEqual('(string->int "00001")', 1)
        self.checkEqual('(string->int "101")', 101)
        self.checkEqual('(string->int "-1")', -1)

        for _ in range(50):
            random_int = random.randint(-99999999, 99999999)
            self.checkEqual(f'(string->int "{random_int}")', random_int)

        with self.assertRaises(WalEvalError):
            self.wal.eval_str('(string->int (quote a))')

        with self.assertRaises(WalEvalError):
            self.wal.eval_str('(string->int 1)')

        with self.assertRaises(WalEvalError):
            self.wal.eval_str('(string->int (array))')

    def test_int_to_string(self):
        '''Test int->string'''

        self.checkEqual('(int->string 0)', '0')
        self.checkEqual('(int->string 1)', '1')
        self.checkEqual('(int->string 00000)', '0')
        self.checkEqual('(int->string 00001)', '1')
        self.checkEqual('(int->string 101)', '101')
        self.checkEqual('(int->string -1)', '-1')

        for _ in range(50):
            random_int = random.randint(-99999999, 99999999)
            self.checkEqual(f'(int->string {random_int})', str(random_int))

        with self.assertRaises(WalEvalError):
            self.wal.eval_str('(int->string (quote a))')

        with self.assertRaises(WalEvalError):
            self.wal.eval_str('(int->string (array))')
