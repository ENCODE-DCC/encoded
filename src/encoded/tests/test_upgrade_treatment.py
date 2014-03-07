import pytest


@pytest.fixture
def treatment():
    return {
        'treatment_type': 'chemical',
        'treatment_term_name': 'ethanol',
    }

@pytest.fixture
def treatment_1(treatment, award):
    item = treatment.copy()
    item.update({
        'schema_version': '1',
        'award': award['uuid'],
    })
    return item


def test_treatment_upgrade(registry, treatment_1):
    migrator = registry['migrator']
    value = migrator.upgrade('treatment', treatment_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'award' not in value    