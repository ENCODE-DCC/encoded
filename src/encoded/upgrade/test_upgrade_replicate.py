import pytest


@pytest.fixture
@pytest.fixture
def replicate(experiment):
    return {
        'experiment': experiment['uuid'],
        'technical_replicate_number': 1,
        'biological_replicate_number': 1
    }


@pytest.fixture
def replicate_1(replicate, library):
    item = replicate.copy()
    item.update({
        'schema_version': '1',
        'library': library['uuid'],
    })
    return item


def test_replicate_upgrade(app, replicate_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('replicate_1', replicate_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == ['released']
