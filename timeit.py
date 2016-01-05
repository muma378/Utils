import time
 
def timefunc(f):
    def f_timer(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print f.__name__, 'took', end - start, 'time'
        return result
    return f_timer
 
def get_number():
    for x in xrange(5000000):
        yield x
 
@timefunc
def expensive_function():
    for x in get_number():
        i = x ^ x ^ x
    return 'some result!'
 
# prints "expensive_function took 0.72583088875 seconds"
result = expensive_function()