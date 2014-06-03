from ..migrator import upgrade_step


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
