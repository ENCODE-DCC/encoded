from contentbase import upgrade_step
from .shared import ENCODE2_AWARDS


@upgrade_step('construct', '', '2')
def construct_0_2(value, system):
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


@upgrade_step('construct', '2', '3')
def construct_2_3(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'tags' in value:
        value['tags'] = list(set(value['tags']))

    if 'documents' in value:
        value['documents'] = list(set(value['documents']))
