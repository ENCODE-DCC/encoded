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
        value['additional_files'] = []
        for file_uuid in value['files']:
            item = root.get_by_uuid(file_uuid)
            if UUID(item.properties['dataset']) != context.uuid:
                value['additional_files'].append(file_uuid)
        del value['files']
