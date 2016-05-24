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
