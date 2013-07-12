from threading3 import SHLock

SPECIAL_NAMES = set([
        '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__', 
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__', 
        '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__', 
        '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__', 
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__', 
        '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__', 
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__', 
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__', 
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__', 
        '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__', 
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__', 
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__', 
        '__truediv__', '__xor__', 'next',
    ])

class UnacquiredLock(Exception):
    pass

def thread_safe(obj, lock, blocking=True, timeout=None):
    class ThreadSafe():
        def __new__(cls):
            def make_method(name):
                def method(self, *args, **kw):
                    return self.__getattribute__(name)(*args, **kw)
                return method
        
            namespace = {}
            for name in SPECIAL_NAMES:
                if hasattr(obj, name):
                    namespace[name] = make_method(name)
                    
            return object.__new__(type("%s(%s)" % (cls.__name__, type(obj).__name__), (cls,), namespace))
        
        def __getattribute__(self, attribute):
            if not lock.acquire(shared=True,blocking=blocking,timeout=timeout):
                raise UnacquiredLock
            try:
                retval = getattr(obj, attribute)
            finally:
                lock.release()
            return retval

        def __setattr__(self, attribute, value):
            if not lock.acquire(shared=False,blocking=blocking,timeout=timeout):
                raise UnacquiredLock
            try:
                retval = setattr(obj, attribute, value)
            finally:
                lock.release()
            return retval

        def __delattr__(self, attribute):
            if not lock.acquire(shared=False,blocking=blocking,timeout=timeout):
                raise UnacquiredLock
            try:
                retval = delattr(obj, attribute)
            finally:
                locks.release()
            return retval

    return ThreadSafe()
