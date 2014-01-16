from ..migrator import upgrade_step


def number(value):
    try:
        return int(value)
    except ValueError:
        return float(value)


@upgrade_step('biosample', '', '2')
def biosample_0_2(value, system):
    # http://redmine.encodedcc.org/issues/794
    if 'starting_amount' in value:
        new_value = number(value['starting_amount'])
        value['starting_amount'] = new_value

