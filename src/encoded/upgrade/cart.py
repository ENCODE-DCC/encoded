from snovault import upgrade_step


@upgrade_step('cart', '1', '2')
def cart_1_2(value, system):
    if 'file_views' not in value:
        value['file_views'] = []
