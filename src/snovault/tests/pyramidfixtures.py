import pytest

# Fixtures  for pyramid, embedding


@pytest.yield_fixture
def config():
    from pyramid.testing import setUp, tearDown
    yield setUp()
    tearDown()


@pytest.yield_fixture
def threadlocals(request, dummy_request, registry):
    from pyramid.threadlocal import manager
    manager.push({'request': dummy_request, 'registry': registry})
    yield manager.get()
    manager.pop()


@pytest.fixture
def dummy_request(root, registry, app):
    from pyramid.request import apply_request_extensions
    request = app.request_factory.blank('/dummy')
    request.root = root
    request.registry = registry
    request._stats = {}
    request.invoke_subrequest = app.invoke_subrequest
    apply_request_extensions(request)
    return request
