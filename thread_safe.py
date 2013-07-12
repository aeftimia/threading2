from threading3 import SHLock, current_thread

SPECIAL_READ_NAMES = set([ '__abs__', '__add__', '__and__', '__call__',
'__cmp__', '__coerce__', '__contains__', '__div__', '__divmod__','__eq__',
'__float__', '__floordiv__', '__ge__', '__getitem__', '__getslice__', '__gt__',
'__hash__', '__hex__','__int__', '__invert__', '__iter__', '__le__', '__len__',
'__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__', '__neg__',
'__oct__', '__or__', '__pos__', '__pow__', '__radd__', '__rand__', '__rdiv__',
'__rdivmod__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__',
'__rfloorfiv__', '__rlshift__', '__rmod__', '__rmul__', '__ror__', '__rpow__',
'__rrshift__', '__rshift__', '__rsub__', '__rtruediv__', '__rxor__', '__sub__',
'__truediv__', '__xor__', 'next', ])

SPECIAL_WRITE_NAMES = set([ '__delitem__', '__delslice__', '__iadd__',
'__iand__','__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__',
'__imod__', '__imul__', '__setitem__', '__setslice__', '__ior__', '__ipow__',
'__irshift__', '__isub__', '__itruediv__', '__ixor__', ])

class UnacquiredLock(Exception):
    pass

def thread_safe(obj, lock, blocking=True, timeout=None):
    class ThreadSafe(object):
        def __new__(cls):
            def make_method(attribute, shared):
                def method(self, *args, **kw):
                    if not lock.acquire(shared=shared, blocking=blocking, timeout=timeout):
                        raise UnacquiredLock
                    assert (current_thread(), shared) in lock._acquire_stack
                    try:
                        retval = getattr(obj, attribute)(*args, **kw)
                    finally:
                        lock.release()
                    return retval
                return method
        
            namespace = {}
            for attribute in SPECIAL_READ_NAMES:
                if hasattr(obj, attribute):
                    namespace[attribute] = make_method(attribute, True)
                    
            for attribute in SPECIAL_WRITE_NAMES:
                if hasattr(obj, attribute):
                    namespace[attribute] = make_method(attribute, False)
                    
            return object.__new__(type("%s(%s)" % (cls.__name__, type(obj).__name__), (cls,), namespace))

        def __getattribute__(self, attribute):
            if not lock.acquire(shared=True, blocking=blocking, timeout=timeout):
                raise UnacquiredLock
            try:
                retval = getattr(obj, attribute)
            finally:
                lock.release()
            return retval

        def __setattr__(self, attribute, value):
            if not lock.acquire(shared=False, blocking=blocking, timeout=timeout):
                raise UnacquiredLock
            try:
                retval = setattr(obj, attribute, value)
            finally:
                lock.release()
            return retval

        def __delattr__(self, attribute):
            if not lock.acquire(shared=False, blocking=blocking, timeout=timeout):
                raise UnacquiredLock
            try:
                retval = delattr(obj, attribute)
            finally:
                lock.release()
            return retval

    return ThreadSafe()
