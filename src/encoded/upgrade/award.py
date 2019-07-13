from snovault import upgrade_step
import re

@upgrade_step('award', '', '2')
def award_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    rfa_mapping = ['ENCODE2', 'ENCODE2-Mouse']
    if value['rfa'] in rfa_mapping:
        value['status'] = 'disabled'
    else:
        value['status'] = 'current'

    # http://encode.stanford.edu/issues/1022
    if 'url' in value:
        if value['url'] == '':
            del value['url']


@upgrade_step('award', '2', '3')
def award_2_3(value, system):
    # http://redmine.encodedcc.org/issues/4743

    if value['viewing_group'] == 'ENCODE':
        value['viewing_group'] = 'ENCODE3'


@upgrade_step('award', '5', '6')
def award_5_6(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4682
    if 'title' not in value:
        value['title'] = value['name']


@upgrade_step('award', '6', '7')
def award_6_7(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4711
    for m in value['milestones']:
        if re.match('single-nuclei ATAC-seq', m):
            new_milestone = m.replace('single-nuclei', 'single-nucleus')
        else:
            continue
        value['milestones'].append(new_milestone)
        value['milestones'].remove(m)
