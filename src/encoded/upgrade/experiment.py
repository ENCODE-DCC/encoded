from ..migrator import upgrade_step


@upgrade_step('experiment', '3', '4')
def experiment_3_4(value, system):
    # http://redmine.encodedcc.org/issues/1393

    if value.get('biosample_type') == 'primary cell line':
        value['biosample_type'] = 'primary cells'