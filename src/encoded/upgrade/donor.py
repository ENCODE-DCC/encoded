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
        elif value['status'] == 'CURRENT' and value['award'] in ENCODE2_AWARDS:
            value['status'] = 'released'
        elif value['status'] == 'CURRENT' and value['award'] not in ENCODE2_AWARDS:
            value['status'] = 'in progress'
