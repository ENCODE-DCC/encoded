from ..migrator import upgrade_step


@upgrade_step('treatment', '', '2')
def treatment_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1182
    
    if 'award' in value:
       del value['award']
