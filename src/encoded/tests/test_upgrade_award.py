import pytest
from unittest import TestCase


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


def test_award_upgrade_viewing_group(upgrader, award_2):
    value = upgrader.upgrade('award', award_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['viewing_group'] == 'ENCODE3'


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
        sorted(value['milestones'], key=lambda x: x['assay_term_name']),
        sorted(
            [
                {'assay_term_name': 'single-nucleus ATAC-seq'},
                {'assay_term_name': 'HiC'}
            ],
            key=lambda x: x['assay_term_name']
        )
    )


def test_award_upgrade_milestones2(upgrader, award_2):
    award_2['schema_version'] = '7'
    award_2['milestones'] = [
        {'assay_term_name': 'single cell isolation followed by RNA-seq'},
        {'assay_term_name': 'RNA-seq'},
    ]
    value = upgrader.upgrade('award', award_2, target_version='8')
    assert value['schema_version'] == '8'
    TestCase().assertListEqual(
        sorted(value['milestones'], key=lambda x: x['assay_term_name']),
        sorted(
            [
                {'assay_term_name': 'single-cell RNA sequencing assay'},
                {'assay_term_name': 'RNA-seq'}
            ],
            key=lambda x: x['assay_term_name']
        )
    )


def test_award_upgrade_milestones3(upgrader, award_8):
    award_8['schema_version'] = '8'
    award_8['milestones'] = [
        {'assay_term_name': 'genotyping by high throughput sequencing assay'},
        {'assay_term_name': 'single-nucleus RNA-seq'},
    ]
    value = upgrader.upgrade('award', award_8, target_version='9')
    assert value['schema_version'] == '9'
    TestCase().assertListEqual(
        sorted(value['milestones'], key=lambda x: x['assay_term_name']),
        sorted(
            [
                {'assay_term_name': 'whole genome sequencing assay'},
                {'assay_term_name': 'single-cell RNA sequencing assay'}
            ],
            key=lambda x: x['assay_term_name']
        )
    )
    assert 'This milestone now lists WGS, upgraded from genotyping HTS assay.' in value['notes']
