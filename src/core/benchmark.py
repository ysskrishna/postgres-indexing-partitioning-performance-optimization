import time

class SimpleBenchmark:    
    @staticmethod
    def timed(func, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        return time.time() - start, result