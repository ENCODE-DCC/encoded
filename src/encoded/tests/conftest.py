'''py.test fixtures for Pyramid.

http://pyramid.readthedocs.org/en/latest/narr/testing.html
'''
from pytest import fixture

settings = {
    'sqlalchemy.url': 'sqlite://',
    }

import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


@fixture
def config(request):
    from pyramid.testing import setUp, tearDown
    request.addfinalizer(tearDown)
    return setUp()


@fixture
def dummy_request():
    from pyramid.testing import DummyRequest
    return DummyRequest()


@fixture
def testapp():
    '''WSGI application level functional testing.
    '''
    from encoded import main
    from webtest import TestApp
    app = main({}, **settings)
    return TestApp(app)


@fixture
def transaction(request):
    import transaction
    request.addfinalizer(transaction.abort)
    return transaction


@fixture
def session(request):
    from encoded.storage import Base, DBSession
    from sqlalchemy import create_engine
    engine = create_engine(settings['sqlalchemy.url'])
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)

    def truncate_all():
        for table in reversed(Base.metadata.sorted_tables):
            engine.execute(table.delete())

    request.addfinalizer(truncate_all)
    return DBSession()
