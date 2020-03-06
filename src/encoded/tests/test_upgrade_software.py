import pytest
from unittest import TestCase


def test_software_upgrade(upgrader, software_upgrade):
    value = upgrader.upgrade('software', software_upgrade, target_version='2')
    assert value['schema_version'] == '2'
    assert value['lab'] == "cb0ef1f6-3bd3-4000-8636-1c5b9f7000dc"
    assert value['award'] == "b5736134-3326-448b-a91a-894aafb77876"


def test_software_upgrade_5_6(upgrader, software_upgrade):
    software_upgrade['schema_version'] = '5'
    software_upgrade['purpose'] = ['single-nuclei ATAC-seq', 'HiC']
    value = upgrader.upgrade('software', software_upgrade, target_version='6')
    assert value['schema_version'] == '6'
    TestCase().assertListEqual(
        sorted(value['purpose']),
        sorted(['single-nucleus ATAC-seq', 'HiC'])
    )
