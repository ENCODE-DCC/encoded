from ..migrator import upgrade_step
from ..views.views import ENCODE2_AWARDS


@upgrade_step('human_donor', '', '2')
@upgrade_step('mouse_donor', '', '2')
def donor_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
        if value['status'] == 'DELETED':
            value['status'] = 'deleted'
        elif value['status'] == 'CURRENT':
            if value['award'] in ENCODE2_AWARDS:
                value['status'] = 'released'
            elif value['award'] not in ENCODE2_AWARDS:
                value['status'] = 'in progress'

@upgrade_step('mouse_donor', '2', '3')
def donor_2_3(value, system):
    # http://encode.stanford.edu/issues/1131

    remove_properties = [
        'sex',
        'parents',
        'children',
        'siblings',
        'fraternal_twin',
        'identical_twin'
    ]

    for remove_property in remove_properties:
        if remove_property in value:
            del value[remove_property]
