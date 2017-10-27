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


@pytest.fixture
def publication_4():
    return {
        'title': 'Fake paper',
        'schema_version': '4'
    }


def test_publication_upgrade(upgrader, publication_1):
    value = upgrader.upgrade('publication', publication_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'references' not in value
    assert value['identifiers'] == ['PMID:25409824']
    assert value['lab'] == "cb0ef1f6-3bd3-4000-8636-1c5b9f7000dc"
    assert value['award'] == "b5736134-3326-448b-a91a-894aafb77876"


def test_publication_upgrade_4_5(upgrader, publication_4):
    publication_4['status'] = 'planned'
    value = upgrader.upgrade('publication', publication_4,
                             current_version='4', target_version='5')
    assert value['status'] == 'in preparation'

    publication_4['status'] = 'replaced'
    value = upgrader.upgrade('publication', publication_4,
                             current_version='4', target_version='5')
    assert value['status'] == 'deleted'

    publication_4['status'] = 'in press'
    value = upgrader.upgrade('publication', publication_4,
                             current_version='4', target_version='5')
    assert value['status'] == 'submitted'

    publication_4['status'] = 'in revision'
    value = upgrader.upgrade('publication', publication_4,
                             current_version='4', target_version='5')
    assert value['status'] == 'submitted'
