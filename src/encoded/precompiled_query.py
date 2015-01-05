# https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/BakedQuery
from functools import wraps

from sqlalchemy.orm.query import Query, _generative, QueryContext


class PrecompiledQuery(Query):
    _precompiled_context = None

    @_generative()
    def precompile_context(self, **kw):
        """
        Compile the current query into a clause and store it into the query for later use.  Note that
        you should not make any more changes to the query that would affect the resulting SQL as those
        changes will not be applied.
        """
        context = super(PrecompiledQuery, self)._compile_context(**kw)
        self._precompiled_context = context
        del context.session
        del context.query

    def _compile_context(self, **kw):
        if self._precompiled_context is not None:
            # Clone the precompiled context and attach it to the current session and query
            # context = self._precompiled_context
            context = QueryContext.__new__(QueryContext)
            context.__dict__.update(self._precompiled_context.__dict__)
            context.query = self
            context.session = self.session
            context.attributes = context.attributes.copy()
            return context
        else:
            return super(PrecompiledQuery, self)._compile_context(**kw)


def precompiled_query_builder(session_getter=None):
    """
    Decorater to wrap a function that builds a query so that the query's SQL will be compiled
    only once for each set of parameters.

    The wrapped function is called only once for each combination of parameters to construct
    the query.  The query builder itself must use bindparams to inserts placeholders for values
    that vary between queries, its own parameters should only be used to guide query construction,
    for example flags as to whether certain fields need to be checked for, and what order to put
    the result.

    The user of the query can then fill in the placeholders by calling the params()
    method on the resulting query.

    :param session_getter: Callable that returns the current SQLALchemy session, given no parameters
    :param f: Query building function
    :return: A Query that will cache the generated SQL
    """
    def decorator(f):
        qry_cache = {}
        compiled_cache = {}

        @wraps(f)
        def wrapper(*args, **kwargs):
            cache_key = (args, tuple(kwargs.items()))
            try:
                qry = qry_cache[cache_key]
            except KeyError:
                qry = f(*args, **kwargs)
                qry = qry.precompile_context().execution_options(compiled_cache=compiled_cache)
                qry_cache[cache_key] = qry
            else:
                if session_getter:
                    qry = qry.with_session(session_getter())
            return qry
        return wrapper
    return decorator


if __name__ == '__main__':
    from sqlalchemy import Column, Integer, String, bindparam, create_engine
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    class Foo(Base):
        __tablename__ = 'foo'
        id = Column(Integer, primary_key=True)
        data = Column(String)

    e = create_engine('sqlite://', echo=True)
    s = Session(e, query_cls=PrecompiledQuery)
    Base.metadata.create_all(e)

    s.add_all([Foo(id=i, data="data: %d" % i) for i in range(100)])

    cache = {}

    @precompiled_query_builder()
    def build_query():
        return s.query(Foo).filter(Foo.data == bindparam('foo'))

    for i in range(10):
        result = build_query().params(foo='data %d' % (i,)).all()
