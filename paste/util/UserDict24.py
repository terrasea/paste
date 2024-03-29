"""A more or less complete user-defined wrapper around dictionary objects."""

class UserDict:
    def __init__(self, dict=None, **kwargs):
        self.data = {}
        if dict is not None:
            if not hasattr(dict,'keys'):
                dict = type({})(dict)   # make mapping from a sequence
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)
    def __repr__(self): return repr(self.data)
    def __cmp__(self, dict):
        if isinstance(dict, UserDict):
            return cmp(self.data, dict.data)
        else:
            return cmp(self.data, dict)
    def __len__(self): return len(self.data)
    def __getitem__(self, key): return self.data[key]
    def __setitem__(self, key, item): self.data[key] = item
    def __delitem__(self, key): del self.data[key]
    def clear(self): self.data.clear()
    def copy(self):
        if self.__class__ is UserDict:
            return UserDict(self.data)
        import copy
        data = self.data
        try:
            self.data = {}
            c = copy.copy(self)
        finally:
            self.data = data
        c.update(self)
        return c
    def keys(self): return list(self.data.keys())
    def items(self): return list(self.data.items())
    def iteritems(self): return iter(self.data.items())
    def iterkeys(self): return iter(self.data.keys())
    def itervalues(self): return iter(self.data.values())
    def values(self): return list(self.data.values())
    def has_key(self, key): return key in self.data
    def update(self, dict):
        if isinstance(dict, UserDict):
            self.data.update(dict.data)
        elif isinstance(dict, type(self.data)):
            self.data.update(dict)
        else:
            for k, v in list(dict.items()):
                self[k] = v
    def get(self, key, failobj=None):
        if key not in self:
            return failobj
        return self[key]
    def setdefault(self, key, failobj=None):
        if key not in self:
            self[key] = failobj
        return self[key]
    def pop(self, key, *args):
        return self.data.pop(key, *args)
    def popitem(self):
        return self.data.popitem()
    def __contains__(self, key):
        return key in self.data
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d
    fromkeys = classmethod(fromkeys)

class IterableUserDict(UserDict):
    def __iter__(self):
        return iter(self.data)

class DictMixin:
    # Mixin defining all dictionary methods for classes that already have
    # a minimum dictionary interface including getitem, setitem, delitem,
    # and keys. Without knowledge of the subclass constructor, the mixin
    # does not define __init__() or copy().  In addition to the four base
    # methods, progressively more efficiency comes with defining
    # __contains__(), __iter__(), and iteritems().

    # second level definitions support higher levels
    def __iter__(self):
        for k in list(self.keys()):
            yield k
    def has_key(self, key):
        try:
            value = self[key]
        except KeyError:
            return False
        return True
    def __contains__(self, key):
        return key in self

    # third level takes advantage of second level definitions
    def iteritems(self):
        for k in self:
            yield (k, self[k])
    def iterkeys(self):
        return self.__iter__()

    # fourth level uses definitions from lower levels
    def itervalues(self):
        for _, v in self.items():
            yield v
    def values(self):
        return [v for _, v in self.items()]
    def items(self):
        return list(self.items())
    def clear(self):
        for key in list(self.keys()):
            del self[key]
    def setdefault(self, key, default):
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default
    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError("pop expected at most 2 arguments, got "\
                              + repr(1 + len(args)))
        try:
            value = self[key]
        except KeyError:
            if args:
                return args[0]
            raise
        del self[key]
        return value
    def popitem(self):
        try:
            k, v = next(iter(self.items()))
        except StopIteration:
            raise KeyError('container is empty')
        del self[k]
        return (k, v)
    def update(self, other):
        # Make progressively weaker assumptions about "other"
        if hasattr(other, 'iteritems'):  # iteritems saves memory and lookups
            for k, v in other.items():
                self[k] = v
        elif hasattr(other, '__iter__'): # iter saves memory
            for k in other:
                self[k] = other[k]
        else:
            for k in list(other.keys()):
                self[k] = other[k]
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    def __repr__(self):
        return repr(dict(iter(self.items())))
    def __cmp__(self, other):
        if other is None:
            return 1
        if isinstance(other, DictMixin):
            other = dict(iter(other.items()))
        return cmp(dict(iter(self.items())), other)
    def __len__(self):
        return len(list(self.keys()))
    
    def __bool__(self):
        return bool(iter(self.items()))
