from ..migrator import upgrade_step


@upgrade_step('file', '', '2')
def file_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307
    if 'status' in value:
        value['status'] = value['status'].lower()


@upgrade_step('file', '2', '3')
def file_2_3(value, system):
    # http://redmine.encodedcc.org/issues/1429
    # http://redmine.encodedcc.org/issues/
    if value.get('status') == 'current':
        if value['experiment'].get('status') == 'released':
            value['status'] = 'released'
        else:
            value['status'] = 'in progress'