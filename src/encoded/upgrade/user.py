from snovault import upgrade_step


@upgrade_step('user', '', '3')
def user_0_3(value, system):
    # http://encode.stanford.edu/issues/1307
    if 'status' in value:
        value['status'] = value['status'].lower()
