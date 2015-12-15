from contentbase import upgrade_step


@upgrade_step('talen', '1', '2')
def talen_1_2(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'documents' in value:
        value['documents'] = list(set(value['documents']))
