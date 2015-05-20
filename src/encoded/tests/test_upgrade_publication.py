import pytest


@pytest.fixture
def publication():
    return{
        'title': "Fake paper"
    }


@pytest.fixture
def publication_1(publication):
    item = publication.copy()
    item.update({
        'schema_version': '1',
        'references': ['PMID:25409824'],
    })
    return item


def test_publication_upgrade(app, publication_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('publication', publication_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'references' not in value
    assert value['identifiers'] == ['PMID:25409824']
    assert value['lab'] == "cb0ef1f6-3bd3-4000-8636-1c5b9f7000dc"
    assert value['award'] == "b5736134-3326-448b-a91a-894aafb77876"
