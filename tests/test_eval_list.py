'''Test wal list eval logic'''
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
