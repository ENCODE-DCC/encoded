from snovault import upgrade_step


@upgrade_step('access_key', '', '2')
def access_key_0_2(value, system):
    # http://encode.stanford.edu/issues/1295
    value['status'] = 'current'
