from snovault import upgrade_step


@upgrade_step('user', '', '3')
def user_0_3(value, system):
    # http://encode.stanford.edu/issues/1307
    if 'status' in value:
        value['status'] = value['status'].lower()


@upgrade_step('user', '3', '4')
def user_3_4(value, system):
    # http://redmine.encodedcc.org/issues/4743
    value['viewing_groups'] = [
        'ENCODE3' if v == 'ENCODE' else v
        for v in value['viewing_groups']
    ]


@upgrade_step('user', '6', '7')
def user_6_7(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3409
    if 'phone1' in value:
        del value['phone1']
    if 'phone2' in value:
        del value['phone2']
    if 'fax' in value:
        del value['fax']
    if 'skype' in value:
        del value['skype']
    if 'google' in value:
        del value['google']
    if 'timezone' in value:
        del value['timezone']


@upgrade_step('user', '7', '8')
def user_7_8(value, system):
    groups = value.get('viewing_groups')
    if groups:
        if 'community' not in groups:
            value['viewing_groups'].append('community')
    else:
        value['viewing_groups'] = ['community']
