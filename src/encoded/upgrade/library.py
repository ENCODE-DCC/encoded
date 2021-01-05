from snovault import upgrade_step


@upgrade_step('library', '1', '2')
def library_1_2(value, system):
    if 'award' in value:
        del value['award']
