# Util/Synchronization.py
'''Simple emulation of Java's 'synchronized'
keyword, from Peter Norvig.'''
import threading

def synchronized(method):
    def _f(*args):
        self = args[0]
        self.mutex.acquire()
        # print(method.__name__, 'acquired')
        try:
            # return apply(method, args)
            return method(*args)
        finally:
            self.mutex.release()
            # print(method.__name__, 'released')
    return _f

def synchronize(klass, names=None):
    """Synchronize methods in the given class.
    Only synchronize the methods whose names are
    given, or all methods if names=None."""
    if type(names)==type(''): 
        names = names.split()
    for (name, val) in klass.__dict__.items():
        if callable(val) and name != '__init__' and (names == None or name in names):
            # print("synchronizing", name)
            setattr(klass, name, synchronized(val))
            # klass.__dict__[name] = synchronized(val)

class Synchronization:
    def __init__(self):
        self.mutex = threading.RLock()