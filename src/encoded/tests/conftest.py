'''py.test fixtures for Pyramid.

http://pyramid.readthedocs.org/en/latest/narr/testing.html
'''
from pytest import fixture

settings = {
    'sqlalchemy.url': 'sqlite://',
    'persona.secret': 'GLIDING LIKE A WHALE',
    'persona.audiences': 'http://localhost:6543',
    'persona.siteName': 'ENCODE DCC Submission',
    'load_test_only': True,
    'load_sample_data': False,
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


@fixture(scope='session')
def testapp():
    '''WSGI application level functional testing.
    '''
    from encoded import main
    from webtest import TestApp
    app = main({}, **settings)
    return TestApp(app)


@fixture
def collection_test():
    return {
        'awards': 37,
        'labs': 41,
        'users': 80,
        'sources': 29,
        'targets': 19,
        'antibody-lots': 18,
        'validations': 31,
        'antibodies': 25,
    }


@fixture
def transaction(request):
    import transaction
    request.addfinalizer(transaction.abort)
    return transaction


@fixture(scope='session')
def engine(request):
    from encoded.storage import Base
    from encoded import configure_engine
    engine = configure_engine(settings)

    def truncate_all():
        for table in reversed(Base.metadata.sorted_tables):
            engine.execute(table.delete())

    request.addfinalizer(truncate_all)
    return engine


@fixture
def session(engine, transaction):
    from encoded.storage import DBSession
    return DBSession()
