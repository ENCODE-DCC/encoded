from snovault import upgrade_step


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
