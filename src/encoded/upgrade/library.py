from ..migrator import upgrade_step
from .shared import ENCODE2_AWARDS


@upgrade_step('library', '', '3')
def library_0_3(value, system):
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


@upgrade_step('library', '3', '4')
def library_3_4(value, system):
    # http://redmine.encodedcc.org/issues/2784
    # http://redmine.encodedcc.org/issues/2560

    if 'paired_ended' in value:
        del value['paired_ended']
