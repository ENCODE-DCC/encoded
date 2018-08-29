from snovault import upgrade_step


@upgrade_step('platform', '', '2')
def platform_0_2(value, system):
    # http://redmine.encodedcc.org/issues/817
    value['dbxrefs'] = []

    if 'encode2_dbxrefs' in value:
        for encode2_dbxref in value['encode2_dbxrefs']:
            new_dbxref = 'UCSC-ENCODE-cv:' + encode2_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['encode2_dbxrefs']

    if 'geo_dbxrefs' in value:
        for geo_dbxref in value['geo_dbxrefs']:
            new_dbxref = 'GEO:' + geo_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['geo_dbxrefs']


@upgrade_step('platform', '2', '3')
def platform_2_3(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
        value['status'] = value['status'].lower()


@upgrade_step('platform', '3', '4')
def platform_3_4(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'dbxrefs' in value:
        value['dbxrefs'] = list(set(value['dbxrefs']))

    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))


@upgrade_step('platform', '6', '7')
def platform_6_7(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3776
    if value.get('status') == 'current':
        value['status'] = 'released'
    elif value.get('status') == 'disabled':
        value['status'] = 'deleted'
