import pytest
from unittest import TestCase


def test_software_upgrade(upgrader, software_1):
    value = upgrader.upgrade('software', software_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['lab'] == "cb0ef1f6-3bd3-4000-8636-1c5b9f7000dc"
    assert value['award'] == "b5736134-3326-448b-a91a-894aafb77876"


def test_software_upgrade_5_6(upgrader, software_1):
    software_1['schema_version'] = '5'
    software_1['purpose'] = ['single-nuclei ATAC-seq', 'HiC']
    value = upgrader.upgrade('software', software_1, target_version='6')
    assert value['schema_version'] == '6'
    TestCase().assertListEqual(
        sorted(value['purpose']),
        sorted(['single-nucleus ATAC-seq', 'HiC'])
    )


def test_software_upgrade_6_7(upgrader, software_1):
    software_1['schema_version'] = '6'
    software_1['purpose'] = ['single cell isolation followed by RNA-seq', 'RNA-seq']
    value = upgrader.upgrade('software', software_1, target_version='7')
    assert value['schema_version'] == '7'
    TestCase().assertListEqual(
        sorted(value['purpose']),
        sorted(['single-cell RNA sequencing assay', 'RNA-seq'])
    )


def test_software_upgrade_7_8(upgrader, software_1):
    software_1['schema_version'] = '7'
    software_1['purpose'] = ['single-nucleus RNA-seq',
                             'genotyping by high throughput sequencing assay']
    value = upgrader.upgrade('software', software_1, target_version='8')
    assert value['schema_version'] == '8'
    TestCase().assertListEqual(
        sorted(value['purpose']),
        sorted(['single-cell RNA sequencing assay',
                'whole genome sequencing assay'])
    )
    assert 'The purpose for this software is now WGS, upgraded from genotyping HTS assay.' in value['notes']


def test_software_upgrade_8_9(upgrader, software_1):
    software_1['schema_version'] = '8'
    software_1['purpose'] = ['single-cell ATAC-seq', 'ATAC-seq']
    value = upgrader.upgrade('software', software_1, target_version='9')
    assert value['schema_version'] == '9'
    TestCase().assertListEqual(
        sorted(value['purpose']),
        sorted(['single-nucleus ATAC-seq', 'ATAC-seq'])
    )
    assert 'The purpose for this software is now snATAC-seq, upgraded from scATAC-seq.' in value['notes']


def test_software_upgrade_9_10(upgrader, software_1):
    software_1['schema_version'] = '9'
    software_1['purpose'] = ['Capture Hi-C', 'HiC']
    value = upgrader.upgrade('software', software_1, target_version='10')
    assert value['schema_version'] == '10'
    TestCase().assertListEqual(
        sorted(value['purpose']),
        sorted(['capture Hi-C', 'HiC'])
    )
