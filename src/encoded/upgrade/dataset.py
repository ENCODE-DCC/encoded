from pyramid.traversal import find_root
from uuid import UUID
from ..migrator import upgrade_step
import re
from ..views.views import ENCODE2_AWARDS


@upgrade_step('experiment', '', '2')
@upgrade_step('dataset', '', '2')
def dataset_0_2(value, system):
    # http://redmine.encodedcc.org/issues/650
    context = system['context']
    root = find_root(context)
    if 'files' in value:
        value['related_files'] = []
        for file_uuid in value['files']:
            item = root.get_by_uuid(file_uuid)
            if UUID(item.properties['dataset']) != context.uuid:
                value['related_files'].append(file_uuid)
        del value['files']


@upgrade_step('experiment', '2', '3')
@upgrade_step('dataset', '2', '3')
def dataset_2_3(value, system):
    # http://redmine.encodedcc.org/issues/817
    value['dbxrefs'] = []

    if 'encode2_dbxrefs' in value:
        for encode2_dbxref in value['encode2_dbxrefs']:
            if re.match('.*wgEncodeEH.*', encode2_dbxref):
                new_dbxref = 'UCSC-ENCODE-hg19:' + encode2_dbxref
            elif re.match('.*wgEncodeEM.*', encode2_dbxref):
                new_dbxref = 'UCSC-ENCODE-mm9:' + encode2_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['encode2_dbxrefs']

    if 'geo_dbxrefs' in value:
        for geo_dbxref in value['geo_dbxrefs']:
            new_dbxref = 'GEO:' + geo_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['geo_dbxrefs']

    if 'aliases' in value:
        for alias in value['aliases']:
            if re.match('ucsc_encode_db:hg19-', alias):
                new_dbxref = alias.replace('ucsc_encode_db:hg19-', 'UCSC-GB-hg19:')
            elif re.match('ucsc_encode_db:mm9-', alias):
                new_dbxref = alias.replace('ucsc_encode_db:mm9-', 'UCSC-GB-mm9:')
            elif re.match('.*wgEncodeEH.*', alias):
                new_dbxref = alias.replace('ucsc_encode_db:', 'UCSC-ENCODE-hg19:')
            elif re.match('.*wgEncodeEM.*', alias):
                new_dbxref = alias.replace('ucsc_encode_db:', 'UCSC-ENCODE-mm9:')
            else:
                continue
            value['dbxrefs'].append(new_dbxref)
            value['aliases'].remove(alias)


@upgrade_step('experiment', '3', '4')
@upgrade_step('dataset', '3', '4')
def dataset_3_4(value, system):
    # http://redmine.encodedcc.org/issues/1074
    if 'status' in value:
        if value['status'] == 'DELETED':
            value['status'] = 'deleted'
        elif value['status'] == 'CURRENT':
            if value['award'] in ENCODE2_AWARDS:
                value['status'] = 'released'
            elif value['award'] not in ENCODE2_AWARDS:
                value['status'] = 'submitted'

    else:
        if value['award'] in ENCODE2_AWARDS:
            value['status'] = 'released'
        elif value['award'] not in ENCODE2_AWARDS:
            value['status'] = 'submitted'


@upgrade_step('experiment', '4', '5')
@upgrade_step('dataset', '4', '5')
def experiment_4_5(value, system):
    # http://redmine.encodedcc.org/issues/1393
    if value.get('biosample_type') == 'primary cell line':
        value['biosample_type'] = 'primary cell'