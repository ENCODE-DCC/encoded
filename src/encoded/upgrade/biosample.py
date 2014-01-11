from ..migrator import upgrade_step


@upgrade_step('biosample', '', '2')
def biosample_0_2(value, system):
    # http://redmine.encodedcc.org/issues/794
    if 'starting_amount' in value:
        new_value = int(value['starting_amount'])
        value['starting_amount'] = new_value

