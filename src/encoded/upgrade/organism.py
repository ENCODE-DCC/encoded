from snovault import upgrade_step


@upgrade_step('organism', '', '2')
def organism_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
        value['status'] = value['status'].lower()


@upgrade_step('organism', '4', '5')
def organism_4_5(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3776
    if value.get('status') == 'current':
        value['status'] = 'released'
    elif value.get('status') == 'disabled':
        value['status'] = 'deleted'
