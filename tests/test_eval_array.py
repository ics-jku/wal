'''Test wal array eval logic'''
from wal.core import Wal
from wal.ast_defs import Operator as Op
from .test_eval import OpTest

# pylint: disable=C0103
# pylint: disable=W0201

class BasicaArrayTest(OpTest):
    '''Test basic array functions such as list creation'''

    def setUp(self):
        self.w = Wal()
        self.w.context = {
            'a1': {
                '0': 'foo',
                '1': 'bar',
                'foo': 0,
                'bar': 1,
                '0-1': 'bar'
            }
        }

    def test_array_construcion(self):
        '''Test constructing arrays'''
        self.checkEqual('(array (1 2))', {'1': 2})
        self.checkEqual('(array (1 2) (3 4))', {'1': 2, '3': 4})
        self.checkEqual('(array (1 (+ 1 1)))', {'1': 2})
        self.checkEqual('(array ((+ 1 1) 2))', {'2': 2})
        self.checkEqual('(array (1 "a"))', {'1': 'a'})
        self.checkEqual('(array ("a" 1))', {'a': 1})

        with self.assertRaises(AssertionError):
            self.w.eval('(array (1))')
        with self.assertRaises(AssertionError):
            self.w.eval('(array (1 2 3))')

    def test_geta(self):
        '''Test accessing arrays'''
        self.checkEqual('(geta (array (1 2) (3 4)) 1)', 2)
        self.checkEqual('(geta (array (1 2) (3 4)) 3)', 4)

        with self.assertRaises(ValueError):
            self.checkEqual('(geta (array (1 2) (3 4)) 4)', 4)

        self.checkEqual("(geta (array (\"a\" 2) ('b 4)) \"a\")", 2)
        self.checkEqual("(geta (array (\"a\" 2) ('b 4)) 'b)", 4)

        self.checkEqual("(geta (array (\"a\" 2) ('a 4)) \"a\")", 4)

        # should fail since geta requires at least 2 arguments
        with self.assertRaises(AssertionError):
            self.w.eval('(geta)')
        with self.assertRaises(AssertionError):
            self.w.eval('(geta x)')
        # should fail since geta requires first argument to be a symbol
        with self.assertRaises(AssertionError):
            self.w.eval('(geta 5 "a")')

    def test_seta(self):
        '''Test modifying arrays'''
        self.checkEqual("(seta (array) 'a 2)", {'a': 2})
        self.checkEqual("(seta (array) \"a\" 2)", {'a': 2})
        self.checkEqual("(seta (array) 12 2)", {'12': 2})
        self.checkEqual("(seta (array ['a 5]) 'a 2)", {'a': 2})

        # should fail since first argument must be a symbol or array
        with self.assertRaises(AssertionError):
            self.w.eval('(seta 0 0)')
        with self.assertRaises(AssertionError):
            self.w.eval('(seta "a" 0)')
        with self.assertRaises(AssertionError):
            self.w.eval("(seta '(1 2) 0)")
        # should fail since keys must be either string or int
        with self.assertRaises(AssertionError):
            self.w.eval("(seta (array) '(1 2) 2)")
        with self.assertRaises(AssertionError):
            self.w.eval("(seta (array) (array) 2)")
        with self.assertRaises(AssertionError):
            self.w.eval("(seta (array) '+ 2)")
