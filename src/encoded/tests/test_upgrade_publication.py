import pytest


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


def test_publication_upgrade_5_6(upgrader, publication_5):
    value = upgrader.upgrade('publication', publication_5, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['status'] == 'in progress'
    
    publication_5['status'] = 'published'
    value = upgrader.upgrade('publication', publication_5, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['status'] == 'released'

    publication_5['status'] = 'submitted'
    value = upgrader.upgrade('publication', publication_5, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['status'] == 'in progress'

    publication_5['status'] = 'deleted'
    value = upgrader.upgrade('publication', publication_5, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['status'] == 'deleted'


def test_publication_upgrade_6_7(
    root,
    testapp,
    upgrader,
    registry,
    publication_6,
    annotation_dataset,
    base_experiment,
    base_experiment_series,
    base_reference,
    functional_characterization_experiment,
    publication_data,
):
    publication_6['schema_version'] = '6'
    publication_6['datasets'] = [
        annotation_dataset['uuid'],
        base_experiment['uuid'],
        base_experiment_series['uuid'],
        base_reference['uuid'],
        functional_characterization_experiment['uuid'],
        publication_data['uuid']
    ]
    context = root.get_by_uuid(publication_6['uuid'])
    value = upgrader.upgrade(
        'publication',
        publication_6,
        registry=registry,
        current_version='6',
        target_version='7',
        context=context,
    )
    assert value['schema_version'] == '7'
    assert len(value['datasets']) == 4
    assert annotation_dataset['uuid'] in value['datasets']
    assert base_experiment['uuid'] in value['datasets']
    assert base_experiment_series['uuid'] not in value['datasets']
    assert base_reference['uuid'] in value['datasets']
    assert functional_characterization_experiment['uuid'] in value['datasets']

    new_publication_data = testapp.get(
        publication_data['@id'] + '@@index-data'
    ).json['object']
    assert publication_6['@id'] in new_publication_data['references']
    new_publication = testapp.get(
        publication_6['@id'] + '@@index-data'
    ).json['object']
    assert publication_data['@id'] in new_publication['publication_data']


def test_publication_upgrade_7_8(upgrader, publication_7):
    value = upgrader.upgrade('publication', publication_7, current_version='7', target_version='8')
    assert value['schema_version'] == '8'
    assert 'Incorrect date_published formatting: 3/30/20' in value['notes']
    assert 'date_published' not in value
