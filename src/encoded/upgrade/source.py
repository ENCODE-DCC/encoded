from snovault import upgrade_step


@upgrade_step('source', '', '2')
def source_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
        value['status'] = value['status'].lower()

    # Remove submitted_by, lab and award from sources, removed prior to migration script
    if 'submitted_by' in value:
        del value['submitted_by']

    if 'lab' in value:
        del value['lab']

    if 'award' in value:
        del value['award']


@upgrade_step('source', '2', '3')
def source_2_3(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))


@upgrade_step('source', '5', '6')
def source_5_6(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3776
    if value.get('status') == 'current':
        value['status'] = 'released'
    elif value.get('status') == 'disabled':
        value['status'] = 'deleted'
