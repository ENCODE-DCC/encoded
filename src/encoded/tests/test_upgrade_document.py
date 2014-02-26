import pytest


@pytest.fixture
def document_0():
    return {
        'references': ['PUBMED:19620212', 'PMID: 19122651']
    }


def test_document_0_upgrade(registry, document_0):
    migrator = registry['migrator']
    value = migrator.upgrade('document', document_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['references'] == ['PMID:19620212', 'PMID:19122651']
