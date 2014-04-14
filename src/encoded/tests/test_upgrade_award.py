import pytest


@pytest.fixture
def award():
    return{
        'name': 'ENCODE2',
    }


@pytest.fixture
def award_1(award):
    item = award.copy()
    item.update({
        'schema_version': '1',
        'rfa': "ENCODE2"
    })
    return item


def test_award_upgrade(app, award_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('award', award_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'disabled'


def test_award_upgrade_encode3(app, award_1):
    migrator = app.registry['migrator']
    award_1['rfa'] = 'ENCODE3'
    value = migrator.upgrade('award', award_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'