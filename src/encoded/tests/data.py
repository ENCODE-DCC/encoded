""" pytest plugin to support data fixtures for sqlalchemy sessions

This works by creating multiple concurrent connections which are then 
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
        self._marker = pytest.mark.use_data
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
            self._factories[fn.__name__] = fn
            #conn, teardown = self.connection_for(name)
            pytest.fixture(scope='session')(fn)
            return fn
        return decorate

    def pytest_namespace(self):
        data = {
            'connection_factory': self.connection_factory,
            'datafixture': self.datafixture,
            'use': self._marker,
        }
        return {'data': data}

    @pytest.mark.tryfirst
    def pytest_runtest_setup(self, item):
        marker = item.keywords.get(self._marker.markname, None)
        if marker is None:
            self._current_connection = None
            return
        name, = marker.args
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
