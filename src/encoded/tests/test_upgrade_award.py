import pytest
from unittest import TestCase

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


@pytest.fixture
def award_5(award_2):
    item = award_2.copy()
    item.update({
        'schema_version': '6',
        'viewing_group': 'ENCODE',
    })
    return item


def test_award_upgrade_title_requirement(upgrader, award_5):
    assert 'title' not in award_5
    value = upgrader.upgrade('award', award_5, target_version='6')
    assert value['title']
    assert value['schema_version'] == '6'


def test_award_upgrade_milestones(upgrader, award_2):
    award_2['schema_version'] = '6'
    award_2['milestones'] = [
        {'assay_term_name': 'single-nuclei ATAC-seq'},
        {'assay_term_name': 'HiC'},
    ]
    value = upgrader.upgrade('award', award_2, target_version='7')
    assert value['schema_version'] == '7'
    TestCase().assertListEqual(
        value['milestones'],
        [
            {'assay_term_name': 'single-nucleus ATAC-seq'},
            {'assay_term_name': 'HiC'}
        ]
    )
