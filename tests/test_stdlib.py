'''Test wal std lib'''
import unittest

from wal.core import Wal
from wal.reader import read_wal_sexpr
from wal.ast_defs import Symbol as S


class TestStdLib(unittest.TestCase):
    '''Test std lib traces'''

    def setUp(self):
        self.w = Wal()

    def checkEqual(self, txt, res):
        '''eval first argument and check if result matches second argument '''
        sexpr = read_wal_sexpr(txt)
        self.assertEqual(self.w.eval(sexpr), res)

    def test_symbol_add(self):
        self.checkEqual("(symbol-add 'a)", S("a"))
        self.checkEqual("(symbol-add \"a\")", S("a"))
        self.checkEqual("(symbol-add 'a \"b\")", S("ab"))
        self.checkEqual("(symbol-add \"a\" 'b)", S("ab"))
        self.checkEqual("(symbol-add 'a 'b)", S("ab"))
        self.checkEqual("(symbol-add 'a 'b 'c)", S("abc"))
        self.checkEqual("(symbol-add 'a 'b 5)", S("ab5"))

    def test_reverse(self):
        self.checkEqual("(reverse '())", [])
        d1 = [5, 4, 3, 2, 1, 0]
        self.w.eval_context.environment.define('d1', d1)
        self.checkEqual("(reverse d1)", list(reversed(d1)))

    def test_filter(self):
        d1 = [1, -1, 5, 0]
        self.w.eval_context.environment.define('d1', d1)
        self.checkEqual("(filter (fn [x] #t) '())", [])
        self.checkEqual("(filter (fn [x] #t) d1)", d1)
        self.checkEqual("(filter (fn [x] #f) d1)", [])
        self.checkEqual("(filter (fn [x] (> x 0)) d1)", [1, 5])
        self.checkEqual("(filter (fn [x] (>= x 0)) d1)", [1, 5, 0])

    def test_sort(self):
        self.checkEqual("(sort '())", [])

        d1 = [5, 4, 3, 2, 1, 0]
        self.w.eval_context.environment.define('d1', d1)
        self.checkEqual("(sort d1)", sorted(d1))

        d2 = [0.9878549883866451, 0.3630841004146459, 0.24054707235462536, 0.810704139479723, 0.008632495769705928, 0.3507143499743923, 0.008202100945166602, 0.8083265344582911, 0.1682464702968881, 0.9215670385992867, 0.8225290649490816, 0.07792254727340464, 0.2159710862466896, 0.9260471863425167, 0.5039314384773605, 0.11794849637353377, 0.21576930735876632, 0.6161577683791525, 0.3246979674735745, 0.29892020487092597, 0.365811556184082, 0.28818770375828695, 0.631230267976378, 0.2640352709296183, 0.009859354545733723, 0.7431431897139924, 0.4646480142870896, 0.41767067842905936, 0.48660648634962167, 0.27934401470050985]
        self.w.eval_context.environment.define('d2', d2)
        self.checkEqual("(sort d2)", sorted(d2))

        d3 = [2.985083115516691, 4.7400205187137985, 0.909180684224796, -4.915339076938174, -3.9490000858501464, -1.8560664973030851, 1.5853221560298012, 0.26734205313593495, -3.377537010105016, 3.5624745106983813]
        self.w.eval_context.environment.define('d3', d3)
        self.checkEqual("(sort d3)", sorted(d3))
