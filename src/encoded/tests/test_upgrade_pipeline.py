import pytest
from unittest import TestCase


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


def test_pipeline_upgrade_7_8(upgrader, pipeline_7):
    value = upgrader.upgrade('pipeline', pipeline_7, current_version='7', target_version='8')
    assert value['schema_version'] == '8'
    assert 'assay_term_name' not in value
    assert value['assay_term_names'] == ['MNase-seq']


def test_pipeline_upgrade_8_9(upgrader, pipeline_8):
    value = upgrader.upgrade('pipeline', pipeline_8, current_version='8', target_version='9')
    assert value['schema_version'] == '9'
    assert value.get('status') == 'released'


def test_pipeline_upgrade_9_10(upgrader, pipeline_8):
    pipeline_8['schema_version'] = '9'
    pipeline_8['assay_term_names'] = ['single-nuclei ATAC-seq', 'HiC']
    value = upgrader.upgrade('pipeline', pipeline_8, target_version='10')
    assert value['schema_version'] == '10'
    TestCase().assertListEqual(
        sorted(value['assay_term_names']),
        sorted(['single-nucleus ATAC-seq', 'HiC'])
    )


def test_pipeline_upgrade_10_11(upgrader, pipeline_8):
    pipeline_8['schema_version'] = '10'
    pipeline_8['assay_term_names'] = ['single cell isolation followed by RNA-seq', 'RNA-seq']
    value = upgrader.upgrade('pipeline', pipeline_8, target_version='11')
    assert value['schema_version'] == '11'
    TestCase().assertListEqual(
        sorted(value['assay_term_names']),
        sorted(['single-cell RNA sequencing assay', 'RNA-seq'])
    )


def test_pipeline_upgrade_11_12(upgrader, pipeline_8):
    pipeline_8['schema_version'] = '11'
    pipeline_8['notes'] = 'Notes'
    pipeline_8['assay_term_names'] = ['single-nucleus RNA-seq',
                                      'genotyping by high throughput sequencing assay']
    value = upgrader.upgrade('pipeline', pipeline_8, target_version='12')
    assert value['schema_version'] == '12'
    TestCase().assertListEqual(
        sorted(value['assay_term_names']),
        sorted(['single-cell RNA sequencing assay',
                'whole genome sequencing assay'])
    )
    assert 'This pipeline is now compatible with scRNA-seq, upgraded from snRNA-seq.' in value['notes']

    pipeline_8['assay_term_names'] = ['single-cell RNA sequencing assay']
    pipeline_8['schema_version'] = '11'
    value.pop('notes')
    value = upgrader.upgrade('pipeline', pipeline_8, target_version='12')
    assert 'notes' not in value
