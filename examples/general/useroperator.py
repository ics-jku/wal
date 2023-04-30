import time

from wal.core import Wal

w = Wal()

# define a new WAL operator
def timeit(seval, args):
    start = time.process_time()
    for arg in args:
        seval.eval(arg)
    return time.process_time() - start

# register the new operator
w.register_operator('timeit', timeit)

res = w.eval_str('''(timeit (define x (sum (range 100000)))
                            (define y (average (range 8237000)))
                            (/ x y))''')
print(res)
