'''Test resoling variables logic'''
import unittest

from wal.core import Wal
from wal.reader import read_wal_sexpr
from wal.passes import resolve
from wal.ast_defs import Symbol as S
from wal.ast_defs import Operator as Op
from wal.ast_defs import WalEvalError


class BasicResolveTest(unittest.TestCase):
    '''Test built-in functions'''

    def setUp(self):
        self.wal = Wal()

    def checkEqual(self, txt, res):
        '''eval first argument and check if result matches second argument '''
        self.assertEqual(resolve(read_wal_sexpr(txt)), res)

    def checkRaises(self, txt):
        '''eval first argument and check if assertion is raised'''
        self.assertRaises(WalEvalError, lambda code: resolve(read_wal_sexpr(code)), txt)

    def test_resolve_num(self):
        '''Test resolution of numbers'''

        self.checkEqual('1', 1)
        self.checkEqual('-5', -5)
        self.checkEqual('1.2', 1.2)
        self.checkEqual('0xff123', 0xff123)

    def test_use_afeter_define(self):
        self.checkEqual('(do (define x 5) x)', [Op.DO, [Op.DEFINE, S('x'), 5], S('x', 0)])
        self.checkEqual('(do (define x 5) (define y 2) y x)', [Op.DO, [Op.DEFINE, S('x'), 5], [Op.DEFINE, S('y'), 2], S('y', 0), S('x', 0)])

    def test_use_in_let(self):
        self.checkEqual('(let ([x 5]) x)', [Op.LET, [[S('x'), 5]], S('x', 0)])
        self.checkEqual('(let ([x 5] [y 2]) x)', [Op.LET, [[S('x'), 5], [S('y'), 2]], S('x', 0)])
        self.checkEqual('(let ([x 5] [y 2]) y x)', [Op.LET, [[S('x'), 5], [S('y'), 2]], S('y', 0), S('x', 0)])
        self.checkEqual('(let ([x 5] [y 2]) (+ y x))', [Op.LET, [[S('x'), 5], [S('y'), 2]], [Op.ADD, S('y', 0), S('x', 0)]])
        self.checkEqual('(let ([x 5]) (let ([y 2]) (+ y x)))', [Op.LET, [[S('x'), 5]], [Op.LET, [[S('y'), 2]], [Op.ADD, S('y', 0), S('x', 1)]]])

    def test_use_after_let(self):
        self.checkEqual('(do (let ([x 5]) x) x)', [Op.DO, [Op.LET, [[S('x'), 5]], S('x', 0)], S('x')])
        self.checkEqual('(do (define y 2) (let ([x 5]) y))', [Op.DO, [Op.DEFINE, S('y'), 2], [Op.LET, [[S('x'), 5]], S('y', 1)]])

    def test_shadow_in_let(self):
        self.checkEqual('(do (define x 2) (let ([x 5]) x) x)', [Op.DO, [Op.DEFINE, S('x'), 2], [Op.LET, [[S('x'), 5]], S('x', 0)], S('x', 0)])

    def test_undefined_symbol_should_stay_symbol(self):
        self.checkEqual('x', S('x'))
        self.checkEqual('(do x)', [Op.DO, S('x')])
        self.checkEqual('(do 5 x)', [Op.DO, 5, S('x')])
        self.checkEqual('(define x x)', [Op.DEFINE, S('x'), S('x')])

    def test_lambda_resolution(self):
        self.checkEqual('(fn [x] x)', [Op.FN, [S('x')], S('x', 0)])
        self.checkEqual('(fn [x] y)', [Op.FN, [S('x')], S('y')])
        self.checkEqual('(do (define y 5) (fn [x] y))', [Op.DO, [Op.DEFINE, S('y'), 5], [Op.FN, [S('x')], S('y', 1)]])
        self.checkEqual('(fn [x] (fn [y] x))', [Op.FN, [S('x')], [Op.FN, [S('y')], S('x', 1)]])
        self.checkEqual('(fn [x] (fn [y] y))', [Op.FN, [S('x')], [Op.FN, [S('y')], S('y', 0)]])
        self.checkEqual('(fn [x y] (fn [y] y))', [Op.FN, [S('x'), S('y')], [Op.FN, [S('y')], S('y', 0)]])
        self.checkEqual('(fn [x y] (fn [z] y))', [Op.FN, [S('x'), S('y')], [Op.FN, [S('z')], S('y', 1)]])

    def test_resolution_in_set(self):
        self.checkEqual('(set [x 5])', [Op.SET, [S('x'), 5]])
        self.checkEqual('(do (define x 0) (set [x 5]))', [Op.DO, [Op.DEFINE, S('x'), 0], [Op.SET, [S('x', 0), 5]]])
        self.checkEqual('(do (define x 0) (set [x x]))', [Op.DO, [Op.DEFINE, S('x'), 0], [Op.SET, [S('x', 0), S('x', 0)]]])
        self.checkEqual('(do (define x 0) (set [x y]))', [Op.DO, [Op.DEFINE, S('x'), 0], [Op.SET, [S('x', 0), S('y')]]])

class ResolveEvalTest(unittest.TestCase):
    '''Test built-in functions'''

    def setUp(self):
        self.wal = Wal()

    def checkEqual(self, txt, res):
        '''eval first argument and check if result matches second argument '''
        self.assertEqual(self.wal.run_str(txt), res)

    def checkRaises(self, txt):
        '''eval first argument and check if assertion is raised'''
        self.assertRaises(WalEvalError, lambda code: self.wal.run_str(code), txt)

    def test_resolve_num(self):
        '''Test resolution of numbers'''

        self.checkEqual('1', 1)
        self.checkEqual('-5', -5)
        self.checkEqual('1.2', 1.2)
        self.checkEqual('0xff123', 0xff123)

    def test_use_afeter_define(self):
        self.checkEqual('(do (define x 5) x)', 5)
        self.checkEqual('(do (define x 5) (define y 2) y x)', 5)

    def test_use_in_let(self):
        self.checkEqual('(let ([x 5]) x)', 5)
        self.checkEqual('(let ([x 5] [y 2]) x)', 5)
        self.checkEqual('(let ([x 5] [y 2]) y x)', 5)
        self.checkEqual('(let ([x 5] [y 2]) (+ y x))', 7)
        self.checkEqual('(let ([x 5]) (let ([y 2]) (+ y x)))', 7)

    def test_use_after_let(self):
        self.checkRaises('(do (let ([x 5]) x) x)')
        self.checkEqual('(do (define y 2) (let ([x 5]) y))', 2)

    def test_shadow_in_let(self):
        self.checkEqual('(do (define x 2) (let ([x 5]) x))', 5)
        self.checkEqual('(do (define x 2) (let ([x 5]) x) x)', 2)

    def test_undefined_symbol_should_stay_symbol(self):
        self.checkRaises('x')
        self.checkRaises('(do x)')
        self.checkRaises('(do 5 x)')
        self.checkRaises('(define x x)')

    def test_lambda_resolution(self):
        self.checkEqual('((fn [x] x) 5)', 5)
        self.checkEqual('(do (define y 5) ((fn [x] y) 2))', 5)
        self.checkEqual('((fn [x] ((fn [y] x) 2)) 1)', 1)
        self.checkEqual('((fn [x] ((fn [y] y) x)) 11)', 11)
        self.checkEqual('((fn [x y] ((fn [y] y) (+ x y))) 22 33)', 55)
        self.checkEqual('((fn [x y] ((fn [z] y) 0)) 22 33)', 33)

    def test_resolution_in_set(self):
        self.checkRaises('(set [x 5])')
        self.checkEqual('(do (define x 0) (set [x 5]))', 5)
        self.checkEqual('(do (define x 0) (set [x x]))', 0)
        self.checkRaises('(do (define x 0) (set [x y]))')
