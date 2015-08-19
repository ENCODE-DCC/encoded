import pytest


@pytest.fixture
def pipeline_1():
    return {
        'schema_version': '1',
        'status': 'active',
        'title': 'Test pipeline',
    }


@pytest.fixture
def pipeline_2(award, lab):
    return {
        'schema_version': '2',
        'status': 'active',
        'title': 'Test pipeline',
        'award': award['uuid'],
        'lab': lab['uuid'],
    }


def test_pipeline_upgrade_1_2(upgrader, pipeline_1):
    value = upgrader.upgrade('pipeline', pipeline_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value.get('award') is not None


def test_pipeline_upgrade_2_3(upgrader, pipeline_2):
    value = upgrader.upgrade('pipeline', pipeline_2, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert 'name' not in value
    assert 'version' not in value
    assert 'end_points' not in value
