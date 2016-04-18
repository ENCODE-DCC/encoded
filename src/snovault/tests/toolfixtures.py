import pytest


# Fixtures  for app

@pytest.fixture
def registry(app):
    return app.registry


@pytest.fixture
def auditor(registry):
    import snovault.interfaces
    return registry[snovault.interfaces.AUDITOR]


@pytest.fixture
def blobs(registry):
    import snovault.interfaces
    return registry[snovault.interfaces.BLOBS]


@pytest.fixture
def calculated_properties(registry):
    import snovault.interfaces
    return registry[snovault.interfaces.CALCULATED_PROPERTIES]


@pytest.fixture
def collections(registry):
    import snovault.interfaces
    return registry[snovault.interfaces.COLLECTIONS]


@pytest.fixture
def connection(registry):
    import snovault.interfaces
    return registry[snovault.interfaces.CONNECTION]


@pytest.fixture
def elasticsearch(registry):
    from snovault.elasticsearch import ELASTIC_SEARCH
    return registry[ELASTIC_SEARCH]


@pytest.fixture
def storage(registry):
    import snovault.interfaces
    return registry[snovault.interfaces.STORAGE]


@pytest.fixture
def root(registry):
    import snovault.interfaces
    return registry[snovault.interfaces.ROOT]


@pytest.fixture
def types(registry):
    import snovault.interfaces
    return registry[snovault.interfaces.TYPES]


@pytest.fixture
def upgrader(registry):
    import snovault.interfaces
    return registry[snovault.interfaces.UPGRADER]
