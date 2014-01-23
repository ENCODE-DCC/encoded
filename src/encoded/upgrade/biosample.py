from ..migrator import upgrade_step


def number(value):
    value = value.lower().replace(' ', '')
    value = value.replace('x10^', 'e')
    if value == 'unknown':
        return None
    try:
        return int(value)
    except ValueError:
        return float(value)


@upgrade_step('biosample', '', '2')
def biosample_0_2(value, system):
    # http://redmine.encodedcc.org/issues/794
    if 'starting_amount' in value:
        new_value = number(value['starting_amount'])
        if new_value is None:
            del value['starting_amount']
        else:
            value['starting_amount'] = new_value
