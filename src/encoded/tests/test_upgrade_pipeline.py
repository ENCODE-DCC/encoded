import pytest


@pytest.fixture
def pipeline():
    return{
        'name': 'mouse',
        'taxon_id': '9031'
    }


@pytest.fixture
def pipeline_1(pipeline):
    item = pipeline.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item


def test_pipeline_upgrade_1(upgrader, pipeline_1):
    value = upgrader.upgrade('pipeline', pipeline_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value.get('award') is not None
