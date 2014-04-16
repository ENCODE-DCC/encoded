from ..migrator import upgrade_step


@upgrade_step('award', '', '2')
def award_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    rfa_mapping = ['ENCODE2', 'ENCODE2-Mouse']
    if value['rfa'] in rfa_mapping:
        value['status'] = 'disabled'
    else:
        value['status'] = 'current'
