from ..migrator import upgrade_step


@upgrade_step('publication', '', '2')
def publication(value, system):
    # http://redmine.encodedcc.org/issues/2591
    value['identifiers'] = []

    if 'references' in value:
        for reference in value['references']:
            value['identifiers'].append(reference)
        del value['references']
