from pyramid.traversal import find_root
from uuid import UUID
from ..migrator import upgrade_step


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
            new_dbxref = 'ucsc_encode_db:' + encode2_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['encode2_dbxrefs']
    
    if 'geo_dbxrefs' in value:
        for geo_dbxref in value['geo_dbxrefs']:
            new_dbxref = 'geo_db:' + geo_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['geo_dbxrefs']
