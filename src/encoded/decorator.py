class classreify(object):
    """ Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it caches the result of the method it
    decorates into the class dict after the first call.  It is, in
    Python parlance, a non-data descriptor.  An example:

    .. code-block:: python

       class Foo(object):
           @classreify
           def jammy(cls):
               print('jammy called')
               return cls.__name__

    And usage of Foo:

    >>> v = Foo.jammy
    'jammy called'
    >>> print(v)
    'Foo'
    >>> Foo.jammy
    'Foo'
    >>> # jammy func not called the second time; using cached value

    Subclasses each see their own cached value:

    >>> class Foo2(Foo):
    ...     pass
    ...
    >>> v = Foo2.jammy
    'jammy called'
    >>> print(v)
    'Foo2'
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:  # pragma: no cover
            pass

    def __get__(self, inst, objtype):
        name = '_%s__%s' % (objtype.__name__, self.wrapped.__name__)
        try:
            return getattr(objtype, name)
        except AttributeError:
            pass
        val = self.wrapped(objtype)
        setattr(objtype, name, val)
        return val
