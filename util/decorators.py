import math
import time
import signal
import functools
from queue import Queue
from threading import Thread
from inspect import signature, Signature  # 2 different things


def getter_setter_gen(name, type_):

    def getter(self):
        return getattr(self, "__" + name)

    def setter(self, value):
        if not isinstance(value, type_):
            raise TypeError("{} attribute must be set to an instance of {}".format(name, type_))
        setattr(self, "__" + name, value)

    return property(getter, setter)

void = type(None)

# decorator that forces variables from a class to be certain types
def attr_check(cls):
    rv = {}
    for key, value in cls.__dict__.items():
        if isinstance(value, type):
            value = getter_setter_gen(key, value)
        rv[key] = value
    # Creates a new class, using the modified dictionary as the class dict:
    new_cls = type(cls)(cls.__name__, cls.__bases__, rv)
    new_cls.__doc__ = cls.__doc__
    return new_cls


def type_check(f):
    def wrapper(*args, **kwargs):
        # Go through the arguments and make sure they are the correct type
        sig = signature(f)
        ba = sig.bind(*args, **kwargs)
        for i, (arg_name, arg_value) in enumerate(ba.arguments.items()):
            if arg_name == 'self':
                continue

            if not isinstance(arg_value, sig.parameters[arg_name].annotation):
                raise TypeError("{} argument {} is of type {}, but should be of type {}"
                                .format(f.__name__, arg_name, type(arg_value), sig.parameters[arg_name].annotation))

        result = f(*args, **kwargs)

        # check that the result is the correct type
        if sig.return_annotation != Signature.empty and not isinstance(result, sig.return_annotation):
            raise TypeError("{} return value {} is of type {}, but should be of type {}"
                            .format(f.__name__, result, type(result), sig.return_annotation))

        return result
    wrapper.__doc__ = f.__doc__
    return wrapper


# Retry decorator with exponential backoff
def retry(tries, delay=3, backoff=2):
    '''Retries a function or method until it returns True.

    delay sets the initial delay in seconds, and backoff sets the factor by which
    the delay should lengthen after each failure. backoff must be greater than 1,
    or else it isn't really a backoff. tries must be at least 0, and delay
    greater than 0.'''

    if backoff <= 1:
        raise ValueError("backoff must be greater than 1")

    tries = math.floor(tries)
    if tries < 0:
        raise ValueError("tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay  # make mutable

            rv = f(*args, **kwargs)  # first attempt
            while mtries > 0:
                if rv is True:  # Done on success
                    return True

                mtries -= 1      # consume an attempt
                time.sleep(mdelay)  # wait...
                mdelay *= backoff  # make future wait longer

                rv = f(*args, **kwargs)  # Try again

            return False  # Ran out of tries :-(
        return f_retry  # true decorator -> decorated function
    return deco_retry  # @retry(arg[, ...]) -> true decorator


def singleton(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


class asynchronous(object):
    def __init__(self, func):
        self.func = func

        def threaded(*args, **kwargs):
            self.queue.put(self.func(*args, **kwargs))

        self.threaded = threaded

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def start(self, *args, **kwargs):
        self.queue = Queue()
        thread = Thread(target=self.threaded, args=args, kwargs=kwargs)
        thread.start()
        return asynchronous.Result(self.queue, thread)

    class NotYetDoneException(Exception):
        def __init__(self, message):
            self.message = message

    class Result(object):
        def __init__(self, queue, thread):
            self.queue = queue
            self.thread = thread

        def is_done(self):
            return not self.thread.is_alive()

        def get_result(self):
            if not self.is_done():
                raise asynchronous.NotYetDoneException('the call has not yet completed its task')

            if not hasattr(self, 'result'):
                self.result = self.queue.get()

            return self.result


class TimeoutError(Exception):
    pass


def timeout(seconds, error_message='Function call timed out'):
    def decorated(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return functools.wraps(func)(wrapper)

    return decorated
