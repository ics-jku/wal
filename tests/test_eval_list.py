'''Test wal list eval logic'''
from wal.core import Wal
from wal.ast_defs import Operator as Op
from .test_eval import OpTest

# pylint: disable=C0103
# pylint: disable=W0201


class BasicListTest(OpTest):
    '''Test basic list functions such as list creation'''

    def test_list_construcion(self):
        '''Test constructing lists'''
        self.checkEqual('(list)', [])
        self.checkEqual('(list 1 2)', [1, 2])
        self.checkEqual('(list (list 1 2) 3)', [[1, 2], 3])

    def test_first_second_last(self):
        '''test accessing list elements'''
        l1 = "'(1 2 3)"
        l2 = "'((1 2) 3)"
        self.checkEqual(f'(first {l1})', 1)
        self.checkEqual(f'(first {l2})', [1, 2])

        self.checkEqual(f'(second {l1})', 2)
        self.checkEqual(f'(second {l2})', 3)

        self.checkEqual(f'(last {l1})', 3)
        self.checkEqual(f'(last {l2})', 3)

        self.checkEqual("(first '(1))", self.w.eval("(last '(1))"))
        self.checkEqual("(second '(1 2))", self.w.eval("(last '(1 2))"))

        for op in [Op.FIRST, Op.SECOND, Op.LAST]:
            with self.assertRaises(AssertionError):
                self.w.eval(f'({op.value})')
            with self.assertRaises(AssertionError):
                self.w.eval(f'({op.value} 1 2)')

        with self.assertRaises(AssertionError):
            self.w.eval("(second '(1))")

    def test_rest(self):
        '''test rest operator'''
        self.checkEqual("(rest '(1 2 3))", [2, 3])
        self.checkEqual("(rest '(1 2))", [2])
        self.checkEqual("(rest '(1))", [])
        self.checkEqual("(rest '())", [])

        with self.assertRaises(AssertionError):
            self.w.eval('(rest)')

    def test_in(self):
        '''test in operator'''
        l1 = "'(1 2 3 4)"
        self.checkEqual(f'(in 1 {l1})', True)
        self.checkEqual(f'(in 1 2 {l1})', True)
        self.checkEqual(f'(in 0 {l1})', False)
        self.checkEqual(f'(in 1 0 {l1})', False)

        self.checkEqual(f'(in "a" {l1})', False)

        with self.assertRaises(AssertionError):
            self.w.eval('(in)')

        with self.assertRaises(AssertionError):
            self.w.eval('(in 1)')

        with self.assertRaises(AssertionError):
            self.w.eval('(in 1 2)')

    def test_map(self):
        '''test map operator'''
        l1 = "'(1 2 3 4)"
        l2 = "'(\"a\" \"b\")"
        f = '(lambda (x) (+ x 1))'
        self.checkEqual(f'(map {f} {l1})', [2, 3, 4, 5])
        self.checkEqual(f'(map {f} {l2})', ['a1', 'b1'])

        with self.assertRaises(AssertionError):
            self.w.eval('(map)')
        with self.assertRaises(AssertionError):
            self.w.eval('(map f)')
        with self.assertRaises(AssertionError):
            self.w.eval(f'(map {l1})')
        with self.assertRaises(AssertionError):
            self.w.eval(f'(map {l1} {f})')
        with self.assertRaises(AssertionError):
            self.w.eval(f'(map {l1} {l2})')
        with self.assertRaises(AssertionError):
            self.w.eval(f'(map {f} {l1} {l2})')


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
        self.checkEqual('(array)', {})
        self.checkEqual('(array (1 2))', {1: 2})
        self.checkEqual('(array (1 2) (3 4))', {1: 2, 3: 4})
        self.checkEqual('(array (1 (+ 1 1)))', {1: 2})
        self.checkEqual('(array ((+ 1 1) 2))', {2: 2})
        self.checkEqual('(array (1 "a"))', {1: 'a'})
        self.checkEqual('(array ("a" 1))', {'a': 1})

        with self.assertRaises(AssertionError):
            self.w.eval('(array (1))')
        with self.assertRaises(AssertionError):
            self.w.eval('(array (1 2 3))')

        # key must be either int or string
        with self.assertRaises(AssertionError):
            self.w.eval("(array ('(1 2) 3))")


#     def test_geta(self):
#         '''Test accessing arrays'''
#         self.assertEqual(self.eval(Op.GETA, [S('a1'), '0']), 'foo')
#         self.assertEqual(self.eval(Op.GETA, [S('a1'), 'foo']), 0)
#         self.assertEqual(
#             self.eval(Op.GETA, [S('a1'), [Op.GETA, S('a1'), '0']]), 0)
#         self.assertEqual(self.eval(Op.GETA, [S('a1'), 0, 1]), 'bar')

#         self.assertEqual(self.eval(Op.GETA, [[Op.ARRAY, 0, 'a'], 0]), 'a')

#         # should fail since geta requires at least 2 arguments
#         with self.assertRaises(AssertionError):
#             self.eval(Op.GETA, [])
#         with self.assertRaises(AssertionError):
#             self.eval(Op.GETA, [S('x')])
#         # should fail since geta requires first argument to be a symbol
#         with self.assertRaises(AssertionError):
#             self.eval(Op.GETA, [5])
#         with self.assertRaises(AssertionError):
#             self.eval(Op.GETA, ['x'])
#         # should fail since geta keys must be either int or str
#         with self.assertRaises(AssertionError):
#             self.eval(Op.GETA, [S('x'), [Op.LIST]])

#     def test_seta(self):
#         '''Test modifying arrays'''
#         self.assertEqual(self.eval(Op.SETA, [S('a2'), 0, 1]), {'0': 1})
#         self.assertEqual(self.eval(Op.GETA, [S('a2'), 0]), 1)
#         self.assertEqual(self.eval(Op.SETA, [S('a2'), 0, 5]), {'0': 5})
#         self.assertEqual(self.eval(Op.GETA, [S('a2'), 0]), 5)
#         self.assertEqual(self.eval(Op.SETA, [S('a2'), 0, 1, 22]), {
#             '0': 5, '0-1': 22})
#         self.assertEqual(self.eval(Op.GETA, [S('a2'), 0, 1]), 22)
#         self.assertEqual(self.eval(Op.SETA, [[Op.GET, 'a2'], 5, 33]), {
#             '0': 5, '0-1': 22, '5': 33})

#         # should fail since first argument must be a symbol or array
#         with self.assertRaises(AssertionError):
#             self.eval(Op.SETA, [0])
#         with self.assertRaises(AssertionError):
#             self.eval(Op.SETA, ['a'])
#         with self.assertRaises(AssertionError):
#             self.eval(Op.SETA, ['a', 1])
#         # should fail since keys must be either string or int
#         with self.assertRaises(AssertionError):
#             self.eval(Op.SETA, [S('a1'), [Op.LIST, 1], 0])
#         with self.assertRaises(AssertionError):
#             self.eval(Op.SETA, [S('a1'), [Op.ARRAY], 0])

#     def test_mapa(self):
#         '''Test map on arrays'''
#         array = [Op.ARRAY, 10, 10, 0, 2]
#         func = [Op.LAMBDA, [S('k'), S('v')], [Op.ADD, S('k'), S('v')]]
#         func_bad1 = [Op.LAMBDA, [S('k')], [Op.ADD, S('k'), S('k')]]
#         func_bad2 = [Op.LAMBDA, [S('k'), S('v'), S('x')], [
#             Op.ADD, S('k'), S('v')]]
#         self.assertEqual(self.eval(Op.MAPA, [func, array]), ['1010', '02'])

#         # should fail since mapa requires two args
#         with self.assertRaises(AssertionError):
#             self.eval(Op.MAPA, [])
#         with self.assertRaises(AssertionError):
#             self.eval(Op.MAPA, [func, array, func])
#         # should fail since mapa requires first arg to be func
#         with self.assertRaises(AssertionError):
#             self.eval(Op.MAPA, [1, array])
#         # should fail since mapa requires second arg to be array
#         with self.assertRaises(AssertionError):
#             self.eval(Op.MAPA, [array, func])
#         # should fail since function must have 2 args
#         with self.assertRaises(AssertionError):
#             self.eval(Op.MAPA, [array, func_bad1])
#         with self.assertRaises(AssertionError):
#             self.eval(Op.MAPA, [array, func_bad2])
