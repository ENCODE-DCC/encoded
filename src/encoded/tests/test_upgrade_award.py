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


def test_award_upgrade(upgrader, award_1):
    value = upgrader.upgrade('award', award_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'disabled'


def test_award_upgrade_encode3(upgrader, award_1):
    award_1['rfa'] = 'ENCODE3'
    value = upgrader.upgrade('award', award_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_award_upgrade_url(upgrader, award_1):
    award_1['url'] = ''
    value = upgrader.upgrade('award', award_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'url' not in value


@pytest.fixture
def award_2(award_1):
    item = award_1.copy()
    item.update({
        'schema_version': '3',
        'viewing_group': 'ENCODE',
    })
    return item


def test_award_upgrade_viewing_group(upgrader, award_2):
    value = upgrader.upgrade('award', award_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['viewing_group'] == 'ENCODE3'
