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
    
@upgrade_step('user', '5', '6')
def user_5_6(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3409
    if 'phone1' in value:
        del value['phone1']
