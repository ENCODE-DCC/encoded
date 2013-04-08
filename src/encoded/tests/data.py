""" pytest plugin to support data fixtures for sqlalchemy sessions

Each data fixture is associated with its own connection.

Data fixtures are registered using the ``pytest.datafixture`` decorator.

The connection_factory is registered using the
``pytest.datafixture_connection_factory`` decorator

Tests and fixtures may require the datafixture like any other fixture, either
specifying in the funcargs or with ``pytest.mark.usefixtures(...)``.
"""

import pytest


def pytest_configure(config):
    data = DataFixtureManager(config)
    config.pluginmanager.register(data, 'data')


class ConnectionProxy(object):
    def __init__(self, manager):
        self._connection_manager = manager

    def __getattr__(self, attr):
        connection = self._connection_manager.connection()
        return getattr(connection, attr)


@pytest.fixture(scope='session')
def connection_proxy(data_fixture_manager):
    return ConnectionProxy(data_fixture_manager)


@pytest.fixture(scope='session')
def data_fixture_manager(request):
    return request.config.pluginmanager.getplugin('data')


@pytest.fixture
def connection(data_fixture_manager):
    return data_fixture_manager.connection()


class DataFixtureManager(object):
    def __init__(self, config):
        self.config = config
        self._factories = {}
        self._fixtures = {}
        self._connections = {}
        self._connection_factory = None
        self._current_connection = None

    @property
    def connection_factory(self):
        """ Register the connection factory
        """
        def decorate(fn):
            self._connection_factory = fn
            return fn
        return decorate

    def connection_for(self, name):
        if name in self._connections:
            conn, teardown = self._connections[name]
            return conn, teardown
        if name is not None:
            factory = self._factories.get(name, None)
            if factory is None:
                raise KeyError(name)
        conn_teardown = self._connection_factory(self.scopefunc)
        conn = conn_teardown.next()

        def teardown():
            # Exhaust the generator
            # This is sort of equivalent to the contextlib.contextmanager
            # decorator, should possibly ``conn_teardown.close()`` instead
            # but then the teardown must be in a try: finally: block (or
            # context manager.)
            for teardown in conn_teardown:
                raise AssertionError('Teardown should not reach here')

        record = (conn, [teardown])
        self._connections[name] = record
        return record

    def pytest_sessionstart(self):
        pass

    def pytest_sessionfinish(self):
        for conn, conn_teardown in self._connections.values():
            for teardown in reversed(conn_teardown):
                teardown()

    @property
    def datafixture(self):
        """ Register a data fixture function
        """
        def decorate(fn):
            name = fn.__name__
            self._factories[name] = fn
            #conn, teardown = self.connection_for(name)

            def wrapper(*args, **kw):
                # This check might be unnecessary
                assert self._current_connection == name
                return fn(*args, **kw)

            wrapper.__wrapped__ = fn
            pytest.fixture(scope='session')(wrapper)
            return wrapper
        return decorate

    def pytest_namespace(self):
        return {
            'datafixture_connection_factory': self.connection_factory,
            'datafixture': self.datafixture,
        }

    @pytest.mark.tryfirst
    def pytest_runtest_setup(self, item):
        fi = getattr(item, '_fixtureinfo', None)
        if fi is not None:
            data_fixtures = [
                name for name in fi.names_closure
                if name in self._factories
            ]
        if not data_fixtures:
            self._current_connection = None
            return
        if len(data_fixtures) != 1:
            raise ValueError('Multiple data fixtures specified: %r' % data_fixtures)
        name, = data_fixtures
        self.use_data_fixture(name, item)

    def use_data_fixture(self, name, item):
        if name not in self._factories:
            pytest.skip("test requires datafixture %r" % name)
            return
        self._current_connection = name
        conn, conn_teardown = self.connection_for(name)
        # Run data fixture
        item._request.getfuncargvalue(name)

    def connection(self):
        name = self._current_connection
        return self.connection_for(name)[0]

    def scopefunc(self):
        return self._current_connection
