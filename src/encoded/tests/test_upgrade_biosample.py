import pytest

@pytest.fixture
def biosample(submitter, lab, award, source, organism):
    return {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:349829',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid'],
    }

@pytest.fixture
def biosample_1(biosample):
    item = biosample.copy()
    item.update({
        'schema_version': '1',
        'starting_amount': '1000',
    })
    return item


def test_biosample_upgrade(app, biosample_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample', biosample_1, target_version='2')
    assert value['starting_amount'] == 1000
    assert value['schema_version'] == '2'
