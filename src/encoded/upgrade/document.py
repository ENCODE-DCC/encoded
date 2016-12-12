from past.builtins import basestring
from snovault import upgrade_step
from .shared import ENCODE2_AWARDS, REFERENCES_UUID
from pyramid.traversal import find_root
import re


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


@upgrade_step('document', '3', '4')
def document_3_4(value, system):
    # http://redmine.encodedcc.org/issues/2591
    context = system['context']
    root = find_root(context)
    publications = root['publications']
    if 'references' in value:
        new_references = []
        for ref in value['references']:
            if re.match('doi', ref):
                new_references.append(REFERENCES_UUID[ref])
            else:
                item = publications[ref]
                new_references.append(str(item.uuid))
        value['references'] = new_references


@upgrade_step('document', '4', '5')
def document_4_5(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'urls' in value:
        value['urls'] = list(set(value['urls']))

    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'references' in value:
        value['references'] = list(set(value['references']))
