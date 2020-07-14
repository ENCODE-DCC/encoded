from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('publication', '', '2')
def publication(value, system):
    # http://redmine.encodedcc.org/issues/2591
    value['identifiers'] = []

    if 'references' in value:
        for reference in value['references']:
            value['identifiers'].append(reference)
        del value['references']

    # http://redmine.encodedcc.org/issues/2725
    # /labs/encode-consortium/
    value['lab'] = "cb0ef1f6-3bd3-4000-8636-1c5b9f7000dc"
    # /awards/ENCODE/
    value['award'] = "b5736134-3326-448b-a91a-894aafb77876"

    if 'dbxrefs' in value:
        unique_dbxrefs = set(value['dbxrefs'])
        value['dbxrefs'] = list(unique_dbxrefs)


@upgrade_step('publication', '2', '3')
def publication_2_3(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'identifiers' in value:
        value['identifiers'] = list(set(value['identifiers']))

    if 'datasets' in value:
        value['datasets'] = list(set(value['datasets']))

    if 'categories' in value:
        value['categories'] = list(set(value['categories']))

    if 'published_by' in value:
        value['published_by'] = list(set(value['published_by']))


# Upgrade 3 to 4 in item.py.


@upgrade_step('publication', '4', '5')
def publication_4_5(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3646
    if value['status'] == 'planned':
        value['status'] = 'in preparation'
    elif value['status'] == 'replaced':
        value['status'] = 'deleted'
    elif value['status'] in ['in press', 'in revision']:
        value['status'] = 'submitted'


@upgrade_step('publication', '5', '6')
def publication_5_6(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3708
    if value['status'] == 'published':
        value['status'] = 'released'
    elif value['status'] == 'submitted':
        value['status'] = 'in progress'
    elif value['status'] == 'in preparation':
        value['status'] = 'in progress'
    else:
        pass


@upgrade_step('publication', '6', '7')
def publication_6_7(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5215
    conn = system['registry'][CONNECTION]
    datasets = value.get('datasets', [])
    new_datasets = []
    for dataset_uuid in datasets:
        dataset_obj = conn.get_by_uuid(dataset_uuid)
        if dataset_obj.item_type in [
            'experiment',
            'annotation',
            'functional_characterization_experiment',
            'reference',
        ]:
            new_datasets.append(dataset_uuid)
        if dataset_obj.item_type == 'publication_data':
            new_data = dataset_obj.upgrade_properties().copy()
            if 'schema_version' in new_data:
                del new_data['schema_version']
            # references is required for PublicationData
            uuid = str(system['context'].uuid)
            if uuid not in new_data['references']:
                new_data['references'].append(uuid)
                dataset_obj.update(new_data)
    if len(new_datasets) == 0:
        value.pop('datasets', None)
    else:
        value['datasets'] = new_datasets


@upgrade_step('publication', '7', '8')
def publication_7_8(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5381
    notes = value.get('notes', '')
    if 'date_published' in value:
        likely_year = value['date_published'][:4]
        if not likely_year.isdigit():
            value['notes'] = (notes + 'Incorrect date_published formatting: ' + value['date_published']).strip()
            value.pop('date_published')


@upgrade_step('publication', '8', '9')
def publication_8_9(value,system):
    # https://encodedcc.atlassian.net/browse/ENCD-5386
    if 'datasets' in value:
        datasets = ', '.join(value['datasets'])
        old_notes = value.get('notes', '')
        value['notes'] = (old_notes + 'Publication datasets: ' + datasets)
        value.pop('datasets')
