import pytest


@pytest.fixture
def source():
    return{
        'title': 'Fake source',
        'name': "fake-source"
    }


@pytest.fixture
def source_1(source, lab, submitter, award):
    item = source.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'lab': lab['uuid'],
        'submitted_by': submitter['uuid'],
        'award': award['uuid']
    })
    return item


def test_source_upgrade(upgrader, source_1):
    value = upgrader.upgrade('source', source_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'
    assert 'award' not in value
    assert 'submitted_by' not in value
    assert 'lab' not in value
