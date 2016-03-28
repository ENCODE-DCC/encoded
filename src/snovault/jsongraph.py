from snovault import Item, Root, CONNECTION
from snovault.elasticsearch.indexer import all_uuids
from past.builtins import basestring
from pyramid.view import view_config


def includeme(config):
    config.scan(__name__)


def uuid_to_ref(obj, path):
    if isinstance(path, basestring):
        path = path.split('.')
    if not path:
        return
    name = path[0]
    remaining = path[1:]
    value = obj.get(name, None)
    if value is None:
        return
    if remaining:
        if isinstance(value, list):
            for v in value:
                uuid_to_ref(v, remaining)
        else:
            uuid_to_ref(value, remaining)
        return
    if isinstance(value, list):
        obj[name] = [
            {'$type': 'ref', 'value': ['uuid', v]}
            for v in value
        ]
    else:
        obj[name] = {'$type': 'ref', 'value': ['uuid', value]}


def item_jsongraph(context, properties):
    properties = properties.copy()
    for path in context.type_info.schema_links:
        uuid_to_ref(properties, path)
    properties['uuid'] = str(context.uuid)
    properties['@type'] = context.type_info.name
    return properties


@view_config(context=Root, request_method='GET', name='jsongraph')
def jsongraph(context, request):
    conn = request.registry[CONNECTION]
    cache = {
        'uuid': {},
    }
    for uuid in all_uuids(request.registry):
        item = conn[uuid]
        properties = item.__json__(request)
        cache['uuid'][uuid] = item_jsongraph(item, properties)
        for k, values in item.unique_keys(properties).items():
            for v in values:
                cache.setdefault(k, {})[v] = {'$type': 'ref', 'value': ['uuid', str(item.uuid)]}
    return cache
