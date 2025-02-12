from wal.core import Wal
import unittest


class BasicOpTest(unittest.TestCase):
    '''Test bitwise operations'''

    def setUp(self):
        self.wal = Wal()

    def checkEqual(self, txt, res):
        '''eval first argument and check if result matches second argument '''
        self.assertEqual(self.wal.eval_str(txt), res)

    def test_bitwise_and(self):
        '''Test band'''
        tests = [{'n': ["1234"], 'r': 1234}, {'n': ["838051", "700310"], 'r': 559490}, {'n': ["20952", "525113", "600227", "740493", "318875"], 'r': 0}]

        for test in tests:
            self.checkEqual(f'(band {" ".join(test["n"])})', test["r"])

    def test_bitwise_or(self):
        '''Test bor'''
        tests = [{'n': ["1234"], 'r': 1234}, {'n': ["838051", "700310"], 'r': 978871}, {'n': ["20952", "525113", "600227", "740493", "318875"], 'r': 1048575}]

        for test in tests:
            self.checkEqual(f'(bor {" ".join(test["n"])})', test["r"])

    def test_bitwise_xor(self):
        '''Test bxor'''
        tests = [{'n': ["1234"], 'r': 1234}, {'n': ["838051", "700310"], 'r': 419381}, {'n': ["20952", "525113", "600227", "740493", "318875"], 'r': 977748}]

        for test in tests:
            self.checkEqual(f'(bxor {" ".join(test["n"])})', test["r"])