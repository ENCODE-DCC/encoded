from snovault import upgrade_step


@upgrade_step('cart', '', '2')
def cart_0_2(value, system):
    if 'file_views' not in value:
        value['file_views'] = []


@upgrade_step('cart', '1', '2')
def cart_1_2(value, system):
    if 'file_views' not in value:
        value['file_views'] = []


@upgrade_step('cart', '2', '3')
def cart_2_3(value, system):
    if value['status'] == 'disabled':
        value['status'] = 'deleted'
    if value['status'] == 'current':
        value['status'] = 'unlisted'
