import logging
import time
import functools

logger = logging.getLogger(__name__)

def clock(func):
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        arg_list = [repr(arg) for arg in args]
        arg_list.extend([f"{key}={value}" for key, value in kwargs.items()])
        arg_str = ', '.join(arg_list)
        logger.debug("Function '%s' with [%s -> %s] took %.4f seconds", func.__name__, arg_str, result, elapsed)
        return result
    return clocked