from snovault import upgrade_step


@upgrade_step('lab', '', '2')
def lab_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
        value['status'] = value['status'].lower()


@upgrade_step('lab', '2', '3')
def lab_2_3(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'awards' in value:
        value['awards'] = list(set(value['awards']))


@upgrade_step('lab', '5', '6')
def lab_5_6(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3776
    if value.get('status') == 'current':
        value['status'] = 'released'
    elif value.get('status') == 'disabled':
        value['status'] = 'deleted'
