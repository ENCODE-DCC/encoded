from ..migrator import upgrade_step
from ..views.views import ENCODE2_AWARDS


def fix_reference(value):
    if not isinstance(value, basestring):
        raise ValueError(value)
    return value.replace('PUBMED:', 'PMID:').replace(' ', '')


@upgrade_step('document', '', '2')
def document_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1259

    if 'references' in value:
        value['references'] = [fix_reference(v) for v in value['references']]


@upgrade_step('document', '2', '3')
def document_2_3(value, system):
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
