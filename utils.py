from __future__ import absolute_import
import time

delta = 20


def remove_noise(data):
    '''Remove noise from set'''
    if not data:
        return data

    l = list(data)
    l.sort()
    base = l[0]
    for i in range(1, len(l)):
        if (l[i] - base < delta):
            data.remove(l[i])
        else:
            base = l[i]

    return data

def to_bool(b):
    '''_to_bool(b) -> bool
        Converts string, containing 'True' or 'False' to corresponding bool
        If b is bool return itself
    '''
    if (isinstance(b, bool)):
        return b

    if (isinstance(b, basestring)):
        if b == 'True':
            return True
        elif b == 'False':
            return False

    raise TypeError('Unexpected value: "True" or "False" expected')

def sleep(step):
    time.sleep(step)

import warnings
import functools

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used.

    It was taken from http://stackoverflow.com/a/30253848"""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning) #turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning) #reset filter
        return func(*args, **kwargs)

    return new_func

def debug_only(func):
    def wrapped(self, *args, **kwargs):
        if not self.debug:
            raise RuntimeError("{} must be called only when ${{DEBUG_MODE}} is True".format(func.__name__))

        return func(self, *args, **kwargs)

    return wrapped

def add_error_info(func):
    def wrapped(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            raise RuntimeError(str(e) + "; {}.{} {}".format(self.__class__.__name__, func.__name__, self.name))

    return wrapped
