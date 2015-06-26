import pytest


@pytest.fixture
def software():
    return{
        "name": "star",
        "title": "STAR",
        "description": "STAR (Spliced Transcript Alignment to a Reference)."
    }


@pytest.fixture
def software_1(software):
    item = software.copy()
    item.update({
        'schema_version': '1',
    })
    return item


def test_software_upgrade(upgrader, software_1):
    value = upgrader.upgrade('software', software_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['lab'] == "cb0ef1f6-3bd3-4000-8636-1c5b9f7000dc"
    assert value['award'] == "b5736134-3326-448b-a91a-894aafb77876"
